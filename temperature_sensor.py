import Adafruit_DHT
from threading import Thread
from time import sleep


class TemperatureSensor(Thread):
    def __init__(self, pin, retries, interval, conn):
        Thread.__init__(self)
        self.pin = pin
        self.retries = retries
        self.interval = interval
        self.conn = conn
        self.sensor = Adafruit_DHT.DHT22
        self.value = None
        self.status = None

    def read(self):
        _, self.value = Adafruit_DHT.read_retry(self.sensor, self.pin, self.retries)
        if self.value is not None:
            self.value = round(self.value, 1)
            if self.value > 80 or self.value < -40:
                self.status = 'INCOHERENT_TEMPERATURE'
            else:
                self.status = 'OK'
        else:
            self.status = 'FAILED_TO_RETRIEVE'
        return self.value, self.status

    def save(self):
        self.conn.save('TEMPERATURE', self.value, self.status)

    def show(self):
        print(f"[TemperatureSensor] Temperature: {self.value:4} - Status: {self.status}")

    def run(self):
        while True:
            self.read()
            self.save()
            sleep(self.interval)
