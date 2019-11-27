import RPi.GPIO as GPIO


class PowerSupplySensor:
    def __init__(self, pin, conn):
        self.pin = pin
        self.conn = conn
        self.origin = None
        self.prev_origin = None
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.IN)

    def get_origin(self):
        self.prev_origin = self.origin
        self.origin = 'BATERIA' if GPIO.input(self.pin) == 0 else 'ALTERNA'

    def run(self):
        self.get_origin()
        if self.prev_origin is not None and (self.prev_origin != self.origin):
            self.log()

    def log(self):
        print(f"[PowerSupplySensor] Origen Actual: {self.origin} ; Origin Previo: {self.prev_origin}")
