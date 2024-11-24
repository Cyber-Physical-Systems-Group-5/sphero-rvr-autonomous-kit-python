import asyncio
import nest_asyncio
from src.utils.camera_servos import CameraServos
from src.controller import Controller
from src.driver import RvrDriver
from src.camera import Camera

# Add compatibility with nested event loops
nest_asyncio.apply()

async def initialize_modules(server_ip, server_port, loop):
    """Initialize and return the required modules."""
    controller = Controller(server_ip, server_port)
    camera_servos = CameraServos()
    driver = RvrDriver(loop)
    camera = Camera()
    return controller, camera_servos, driver, camera

async def process_commands(controller, driver, camera_servos, camera):
    """Process commands from the controller and execute actions concurrently."""
    try:
        proto_message = controller.read_message()
        #print(f"dir = {proto_message.directions}")
        #print(f"c_dir = {proto_message.camera_directions}")

        driver.update_controls(proto_message)

        # Schedule camera and driver operations concurrently
        capture_image_task = asyncio.create_task(camera.capture_image())
        camera_task = asyncio.create_task(camera_servos.move_camera(proto_message))
        drive_task = asyncio.create_task(driver.drive())

        # Wait for both tasks to complete
        await asyncio.gather(camera_task, drive_task, capture_image_task)
    except Exception as e:
        print(f"Error processing commands: {e}")

async def main(server_ip, server_port):
    """Main function to initialize modules and run the control loop."""
    loop = asyncio.get_event_loop()
    controller, camera_servos, driver, camera = await initialize_modules(server_ip, server_port, loop)

    try:
        print("Trying to connect to server...")
        controller.connect()
        print("Connected to server")

        # Wake up the RVR
        await driver.wake()

        print("Starting command processing loop...")
        while True:
            await process_commands(controller, driver, camera_servos, camera)
    except KeyboardInterrupt:
        print("Program stopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        controller.close()
        print("Server connection closed.")

if __name__ == "__main__":
    SERVER_IP = "192.168.0.172"  # Server IP address
    SERVER_PORT = 8000  # Server port

    try:
        asyncio.run(main(SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"Fatal error in main: {e}")
