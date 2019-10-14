import RPi.GPIO as GPIO


class DeviceController:
    def __init__(self, pin):
        self.pin = pin
        self.state = 0
        self.conditions = []
        GPIO.setup(self.pin, GPIO.OUT)

    def add_condition(self, condition):
        self.conditions.append(condition)

    def verify_conditions(self, value, c_type):
        for condition in self.conditions:
            if condition(value, c_type):
                return self.set_state(1)
        self.set_state(0)

    def get_state(self):
        return self.state

    def set_state(self, state):
        GPIO.output(self.pin, state)
        self.state = state
