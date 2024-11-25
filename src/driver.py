from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync
from src.utils.directions import Direction
import asyncio

class RvrDriver:
    def __init__(self, loop):
        self.loop = loop
        self.rvr = SpheroRvrAsync(dal = SerialAsyncDal(self.loop))
        self.heading_step = 10

        self.speed = 0
        self.heading = 0
        self.flags = 0
    
    async def wake(self):
        """Wake up the RVR and reset its yaw."""
        await self.rvr.wake()
        await self.rvr.reset_yaw()
    
    def get_battery_percentage(self):
        """Return the battery percentage of the RVR."""
        return self.rvr.get_battery_percentage()
    
    def update_controls(self, proto_message):
        """Drive the RVR at the given speed and direction."""
        if (len(proto_message.directions) == 0):
            return
        direction = proto_message.directions[0]
        self.speed = proto_message.speed
        if direction == Direction.FORWARD:
            self.flags = 0
        elif direction == Direction.BACKWARD:
            self.flags = 1
        elif direction == Direction.LEFT:
            self.heading += self.heading_step
        elif direction == Direction.RIGHT:
            self.heading -= self.heading_step
        else:
            self.speed = 0
            self.flags = 0
        
        if self.heading > 360:
            self.heading -= 360
        elif self.heading < 0:
            self.heading += 360

    async def drive(self):
        """Drive the RVR according to the current controls."""
        await self.rvr.drive_with_heading(speed = self.speed, heading = self.heading, flags = self.flags)
        await asyncio.sleep(0.1)