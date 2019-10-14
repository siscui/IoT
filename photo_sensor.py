from math import cos, pi
from threading import Thread
from time import sleep


class PhotoSensor(Thread):
    def __init__(self, spi, pin, conn, interval):
        Thread.__init__(self)
        self.spi = spi
        self.pin = pin
        self.conn = conn
        self.interval = interval
        self.value = None
        self.status = None

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
        else:
            self.status = 'CANNOT_READ_LDR'
        return self.value, self.status

    def show(self):
        print(f"[PhotoSensor] Value: {self.value:5} - Status: {self.status}")

    def save(self):
        self.conn.save('ILLUMINATION', self.value, self.status)

    def run(self):
        while True:
            self.read()
            self.show()
            self.save()
            sleep(self.interval)
