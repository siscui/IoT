from math import cos, pi
import spidev

class PhotoSensor:
    def __init__(self, spi):
        self.spi = spi
        self.pin = 0
        self.value = None
        self.status = None

    def read(self):
        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        r = self.spi.xfer2([1, 8 + self.pin << 4, 0])
        self.value = ((r[1] & 3) << 8) + r[2]
        if self.value is not None:
            if self.value > 1023 or self.value < 0:
                self.status = "ERR_LUZ_2"
            else:
                self.status = "OK"
                self.value = round(50 * (cos(pi * self.value / 1023) + 1))
        else:
            self.status = 'ERR_LUZ_1'  # No se pudo leer el LDR
        conn.save_sensor("ILUMINACIONES", self.value, self.status)
        return self.value, self.status

    def mostrar(self):
        print(f"Luz: {self.value:5}  - STATUS: {self.status}")
