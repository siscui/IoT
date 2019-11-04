import Adafruit_DHT
from threading import Thread
from time import sleep


class TemperatureSensor(Thread):
    def __init__(self, pin, lamp, conn):
        Thread.__init__(self)
        self.pin = pin
        self.retries = 5
        self.lamp = lamp
        self.conn = conn
        self.sensor = Adafruit_DHT.DHT22
        self.value = None
        self.status = None
        self.timestamp = None

    def set_min_max(self, min_temperature, max_temperature):
        self.lamp.add_condition(
            lambda temperature, c_type: min_temperature > temperature < max_temperature and c_type == 'temperature')

    def unset_min_max(self):
        self.lamp.reset()

    def read(self):
        _, self.value = Adafruit_DHT.read_retry(self.sensor, self.pin, self.retries)
        if self.value is not None:
            self.value = round(self.value, 1)
            if self.value > 80 or self.value < -40:
                self.status = 'INCOHERENT_READ'
            else:
                self.status = 'OK'
                self.lamp.verify_conditions(self.value, 'temperature')
        else:
            self.status = 'FAILED_TO_RETRIEVE'
        return self.value, self.status

    def save(self):
        self.timestamp = self.conn.save('TEMPERATURE', {'value': self.value, 'status': self.status})

    def log(self):
        print(f"[TemperatureSensor] Temperature: {self.value} - Status: {self.status} - Timestamp: {self.timestamp}")

    def run(self):
        self.read()
        self.save()
        self.log()