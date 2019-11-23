from math import cos, pi
from device_controller import DeviceController


class PhotoSensor:
    def __init__(self, spi, pin, conn, lamp_pin):
        self.spi = spi
        self.pin = pin
        self.conn = conn
        self.lamp = DeviceController(pin=lamp_pin)
        self.value = None
        self.status = None
        self.timestamp = None
        self.force = False

    def set_min_max(self, min_illumination, max_illumination):
        self.lamp.add_condition(lambda photo, c_type: min_illumination > photo and c_type == 'photo')

    def unset_min_max(self):
        self.lamp.reset()

    def set_lamp_state(self, state):
        if self.force is False:
            self.lamp.set_state(state)

    def get_lamp_state(self):
        return self.lamp.get_state()

    def read(self):
        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        r = self.spi.xfer2([1, 8 + self.pin << 4, 0])
        self.value = ((r[1] & 3) << 8) + r[2]
        if self.value is not None:
            if self.value > 1023 or self.value < 0:
                self.status = 'VALUE_OUT_OF_BOUNDS'
            else:
                self.status = 'OK'
                self.value = round(50 * (cos(pi * self.value / 1023) + 1))
                if self.force is False:
                    self.lamp.verify_conditions(self.value, 'photo')
        else:
            self.status = 'CANNOT_READ_LDR'
        return self.value, self.status

    def save(self):
        self.timestamp = self.conn.save('ILLUMINATION', {'value': self.value, 'status': self.status})

    def log(self):
        print(f"[PhotoSensor] Value: {self.value} - Status: {self.status} - Timestamp: {self.timestamp}")

    def run(self, force):
        self.force = force
        self.read()
        self.save()
        self.log()
        return self.get_lamp_state()
