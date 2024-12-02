from PIL import Image
import socket
import io
import time
import asyncio
from picamera2 import Picamera2
import protobuf.message_pb2 as message_pb2


class Camera:
    def __init__(self, width=320, height=240):
        self.camera = Picamera2()

        self.configuration = self.camera.create_preview_configuration(
            main={"size": (width, height), "format": "BGR888"},
            raw={"size": (width, height)}
        )

        self.camera.configure(self.configuration)
        self.camera.start()
        time.sleep(2)
    
    def capture_image(self):
        """Capture an image and return it as a protobuf message."""
        array = self.camera.capture_array("main")
        image = Image.fromarray(array, 'RGB')
        # Convert to PNG
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=50)
        # Create protobuf message
        message = message_pb2.ProtoMessage()
        message.image = buffer.getvalue()
        return message
    
    def __stop(self):
        self.camera.stop()

    def __del__(self):
        self.__stop()