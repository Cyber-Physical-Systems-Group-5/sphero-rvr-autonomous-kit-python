from src.utils.camera_servos import CameraServos
from src.controller import Controller
from src.driver import RvrDriver
import asyncio

def main(server_ip, server_port):
    controller = Controller(server_ip, server_port)
    camera_servos = CameraServos()
    driver = RvrDriver()
    try:
        print("Trying to connect to server...")
        controller.connect()
        print("Connected to server")

        # Wake up the RVR
        asyncio.run(driver.wake())

        while True:
            #image_data = capture_image(camera)
            #protobuf_data = create_protobuf_message(image_data)
            #length_prefix = len(protobuf_data).to_bytes(4, 'big')
            #sock.sendall(length_prefix)
            #sock.sendall(protobuf_data)
            try:
                proto_message = controller.read_message()
                driver.update_controls(proto_message)
                asyncio.run(camera_servos.move_camera(proto_message))
                asyncio.run(driver.drive())
            except Exception as e:
                print(f"Error: {e}")


    except KeyboardInterrupt:
        print("Program Stopped.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.close()
        print("Server closed.")

if __name__ == "__main__":
    SERVER_IP = "192.168.0.172"  # Server IP address
    SERVER_PORT = 8000  # Server port
    try:
        main(SERVER_IP, SERVER_PORT)
    finally:
        print("Input stopped.")
