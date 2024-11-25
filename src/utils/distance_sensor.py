import board
import busio
from adafruit_vl53l1x import VL53L1X


class DistanceSensor:
    def __init__(self):
        # Initialize the I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = VL53L1X(self.i2c)

        # Initialze the sensor
        self.sensor.start_ranging()

    def get_distance(self):
        return self.sensor.distance

    def __del__(self):
        self.sensor.stop_ranging()

