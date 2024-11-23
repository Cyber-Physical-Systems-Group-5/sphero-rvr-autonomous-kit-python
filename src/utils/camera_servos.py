import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from src.utils.directions import Direction

class CameraServos:
    # Initialize the I2C bus.
    i2c = busio.I2C(board.SCL, board.SDA)
    ANGLE_STEP = 5
    # constructor
    def __init__(self):
        # Initialize the PCA9685 module (on the Servo pHAT).
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50  # Set the frequency to 50 Hz, which is standard for many servos.

        # Initialize servos on channel 0 and channel 1.
        self.servo_0 = servo.Servo(self.pca.channels[0])
        self.servo_1 = servo.Servo(self.pca.channels[1])

        # Move camera to starting position
        self.set_angles(90, 90)
    
    def set_angles(self, angle_0, angle_1):
        self.servo_0.angle = angle_0  # Set the servo on channel 0 to the desired angle.
        self.servo_1.angle = angle_1  # Set the servo on channel 1 to the desired angle.
        time.sleep(3)            # Wait 1 second to allow the servos to reach their positions.
    
    async def move_camera(self, proto_message):
        direction = proto_message.camera_directions[0]
        if (direction == Direction.FORWARD):
            self.servo_1.angle += self.ANGLE_STEP
        elif (direction == Direction.BACKWARD):
            self.servo_1.angle -= self.ANGLE_STEP
        elif (direction == Direction.LEFT):
            self.servo_0.angle -= self.ANGLE_STEP
        elif (direction == Direction.RIGHT):
            self.servo_0.angle += self.ANGLE_STEP
    # destructor
    def __del__(self):
        # Set both servos to 90 degrees at the end.
        self.set_angles(90, 90)       # Set both servos to 90 degrees.
        self.pca.deinit()             # Shut down the PCA9685 module.
