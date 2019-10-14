import Adafruit_DHT
from threading import Thread
from time import sleep


class TemperatureSensor(Thread):
    def __init__(self, pin, retries, lamp, interval, conn, min, max):
        Thread.__init__(self)
        self.pin = pin
        self.retries = retries
        self.lamp = lamp
        self.interval = interval
        self.conn = conn
        self.sensor = Adafruit_DHT.DHT22
        self.value = None
        self.status = None
        self.timestamp = None
        self.lamp.add_condition(lambda temperature, c_type: min > temperature < max and c_type == 'temperature')

    def read(self):
        _, self.value = Adafruit_DHT.read_retry(self.sensor, self.pin, self.retries)
        if self.value is not None:
            self.value = round(self.value, 1)
            if self.value > 80 or self.value < -40:
                self.status = 'INCOHERENT_READ'
            else:
                self.status = 'OK'
                self.lamp.validate(self.value, 'temperature')
        else:
            self.status = 'FAILED_TO_RETRIEVE'
        return self.value, self.status

    def save(self):
        self.timestamp = self.conn.save('TEMPERATURE', {'value': self.value, 'status': self.status})

    def log(self):
        print(f"[TemperatureSensor] Temperature: {self.value:4} - Status: {self.status} - Timestamp: {self.timestapm}")

    def run(self):
        while True:
            self.read()
            self.log()
            self.save()
            sleep(self.interval)
