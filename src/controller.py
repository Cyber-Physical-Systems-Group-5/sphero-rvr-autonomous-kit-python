import socket
import struct
import time
import asyncio
import protobuf.message_pb2 as message_pb2
from src.utils.distance_sensor import DistanceSensor

# Component used to handle communication with the server
class Controller:
    def __init__(self, server_ip, server_port, camera):
        self.camera = camera
        self.retry_interval = 5
        self.server_ip = server_ip
        self.server_port = server_port
        self.distance_sensor = DistanceSensor()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
    
    def connect(self):
        while True:
            try:
                print(f"Trying to connect to {self.server_ip}:{self.server_port}...")
                self.sock.connect((self.server_ip, self.server_port))
                print("Connected to the server!")
                break  # Exit the loop once connected
            except socket.error as e:
                print(f"Connection failed: {e}. Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

    def close(self):
        self.sock.close()
    
    async def read_message(self):
        # if there is no connection, raise an error
        if not self.sock:
            raise ValueError("No connection to server")
        
        # Read the message
        try:
            # Read the length prefix (4 bytes)
            length_prefix = await asyncio.get_event_loop().sock_recv(self.sock, 4)
            if len(length_prefix) < 4:
                raise ValueError("Incomplete length prefix received")

            # Unpack the length prefix to get the message size
            message_length = struct.unpack('<I', length_prefix)[0]  # '<I' is little-endian uint32

            # Read the message
            message_data = b""
            while len(message_data) < message_length:
                chunk = await asyncio.get_event_loop().sock_recv(self.sock, message_length - len(message_data))
                if not chunk:
                    raise ValueError("Connection closed before full message was received")
                message_data += chunk

            # Deserialize the message
            proto_message = message_pb2.ProtoMessage()
            proto_message.ParseFromString(message_data)
            return proto_message
        except Exception as e:
            print(f"Error reading message: {e}")
            return None
    
    async def send_data(self, send_image=True, battery_percentage=0, distance=0):
        proto_message = message_pb2.ProtoMessage()
        # Capture an image
        if (send_image):
            proto_message = self.camera.capture_image()
        else:
            # Include distance data
            proto_message.distance = self.distance_sensor.get_distance()
            # Include battery percentage
            proto_message.battery_percentage = battery_percentage
        # Send the message
        self.__send_message(proto_message)
    
    def __send_message(self, proto_message):
        # if there is no connection, raise an error
        if not self.sock:
            raise ValueError("No connection to server")
        
        serialized_message = proto_message.SerializeToString()
        
        # Send prefix and message
        length_prefix = len(serialized_message).to_bytes(4, 'big')

        self.sock.sendall(length_prefix)
        self.sock.sendall(serialized_message)