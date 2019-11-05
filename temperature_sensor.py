import Adafruit_DHT
from device_controller import DeviceController


class TemperatureSensor:
    def __init__(self, pin, heater_pin, conn):
        self.pin = pin
        self.retries = 5
        self.heater = DeviceController(pin=heater_pin)
        self.conn = conn
        self.sensor = Adafruit_DHT.DHT22
        self.value = None
        self.status = None
        self.timestamp = None
        self.force = False

    def set_min_max(self, min_temperature, max_temperature):
        self.heater.add_condition(
            lambda temperature, c_type: min_temperature < temperature < max_temperature and c_type == 'temperature')

    def unset_min_max(self):
        self.heater.reset()

    def set_heater_state(self, state):
        if self.force is False:
            self.heater.set_state(state)

    def get_heater_state(self):
        return self.heater.get_state()

    def read(self):
        _, self.value = Adafruit_DHT.read_retry(self.sensor, self.pin, self.retries)
        if self.value is not None:
            self.value = round(self.value, 1)
            if self.value > 80 or self.value < -40:
                self.status = 'INCOHERENT_READ'
            else:
                self.status = 'OK'
                self.heater.verify_conditions(self.value, 'temperature')
        else:
            self.status = 'FAILED_TO_RETRIEVE'
        return self.value, self.status

    def save(self):
        self.timestamp = self.conn.save('TEMPERATURE', {'value': self.value, 'status': self.status})

    def log(self):
        print(f"[TemperatureSensor] Temperature: {self.value} - Status: {self.status} - Timestamp: {self.timestamp}")

    def run(self, force):
        self.force = force
        self.read()
        self.save()
        self.log()
