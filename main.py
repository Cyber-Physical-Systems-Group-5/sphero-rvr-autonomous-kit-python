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
    camera = Camera()
    controller = Controller(server_ip, server_port, camera)
    camera_servos = CameraServos()
    driver = RvrDriver(loop)
    return controller, camera_servos, driver, camera

async def process_commands(controller, driver, camera_servos, camera):
    """Process commands from the controller and execute actions concurrently."""
    try:
        # Create a task for reading messages
        read_message_task = asyncio.create_task(controller.read_message())
        # Proceed with other tasks concurrently
        while True:
            proto_message = None
            # Attempt to get the next message without blocking
            if read_message_task.done():
                proto_message = read_message_task.result()
                if proto_message is not None:
                    print(f"Received proto_message: {proto_message}")
                    driver.update_controls(proto_message)

                # Restart the read_message_task for the next message
                read_message_task = asyncio.create_task(controller.read_message())

            # Schedule other tasks
            send_data_task = asyncio.create_task(controller.send_data())
            drive_task = asyncio.create_task(driver.drive())

            # Only move the camera if there is a message
            if proto_message:
                camera_task = asyncio.create_task(camera_servos.move_camera(proto_message))
                await asyncio.gather(camera_task, drive_task, send_data_task)
            else:
                await asyncio.gather(drive_task, send_data_task)

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
    SERVER_IP = "10.22.88.217"  # Server IP address
    SERVER_PORT = 8000  # Server port

    try:
        asyncio.run(main(SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"Fatal error in main: {e}")