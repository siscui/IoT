import RPi.GPIO as GPIO

ON_STATE = 0
OFF_STATE = 1

class DeviceController:
    def __init__(self, pin):
        self.pin = pin
        self.state = 0
        self.conditions = []
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

    def add_condition(self, condition):
        self.conditions.append(condition)

    def verify_conditions(self, value, c_type):
        for condition in self.conditions:
            if condition(value, c_type):
                return self.set_state(ON_STATE)
        self.set_state(OFF_STATE)

    def get_state(self):
        return self.state

    def set_state(self, state):
        GPIO.output(self.pin, state)
        self.state = state
