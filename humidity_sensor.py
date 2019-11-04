from math import cos, pi
from time import sleep


class HumiditySensor:
    def __init__(self, spi, pin, conn, pump):
        self.pin = pin
        self.spi = spi
        self.conn = conn
        self.pump = pump
        self.value = None
        self.status = None
        self.timestamp = None

    def set_min_max(self, min_humidity, max_humidity):
        self.pump.add_condition(
            lambda humidity, c_type: min_humidity > humidity < max_humidity and c_type == 'humidity')

    def unset_min_max(self):
        self.pump.reset()

    def read(self):
        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        r = self.spi.xfer2([1, 8 + self.pin << 4, 0])
        self.value = ((r[1] & 3) << 8) + r[2]
        if self.value is not None:
            if self.value > 1023 or self.value < 0:
                self.status = 'INCOHERENT_READ'
            else:
                self.value = round(50 * (cos(pi * self.value / 1023) + 1))
                self.status = 'OK'
                self.pump.verify_conditions(self.value, 'humidity')
        else:
            self.status = 'FAILED_TO_RETRIEVE'
        return self.value, self.status

    def save(self):
        self.timestamp = self.conn.save('HUMIDITY', {'value': self.value, 'status': self.status})

    def log(self):
        print(f"[HumiditySensor] Humidity: {self.value} - Status: {self.status} - Timestamp: {self.timestamp}")

    def run(self):
        self.read()
        self.save()
        self.log()