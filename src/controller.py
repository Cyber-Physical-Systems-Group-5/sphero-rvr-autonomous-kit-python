import socket
import struct
import time
import protobuf.message_pb2 as message_pb2

# Component used to handle communication with the server
class Controller:
    def __init__(self, server_ip, server_port):
        self.retry_interval = 5
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
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
    
    def read_message(self):
        # if there is no connection, raise an error
        if not self.sock:
            raise ValueError("No connection to server")
        
        # Read the message

        # Read the length prefix (4 bytes)
        length_prefix = self.sock.recv(4)
        if len(length_prefix) < 4:
            raise ValueError("Incomplete length prefix received")

        # Unpack the length prefix to get the message size
        message_length = struct.unpack('<I', length_prefix)[0]  # '<I' is little-endian uint32

        # Read the message
        message_data = b""
        while len(message_data) < message_length:
            chunk = self.sock.recv(message_length - len(message_data))
            if not chunk:
                raise ValueError("Connection closed before full message was received")
            message_data += chunk

        # Deserialize the message
        proto_message = message_pb2.ProtoMessage()
        proto_message.ParseFromString(message_data)

        return proto_message