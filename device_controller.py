import RPi.GPIO as GPIO
from time import sleep

ON_STATE = 0
OFF_STATE = 1


class DeviceController:
    def __init__(self, pin, duration=None):
        self.pin = pin
        self.state = 1
        self.conditions = []
        self.duration = duration
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT, initial=1)

    def add_condition(self, condition):
        self.conditions.append(condition)

    def reset(self):
        self.conditions = []

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
        if self.duration is not None and state == ON_STATE:
            sleep(self.duration)
            GPIO.output(self.pin, OFF_STATE)
            self.state = OFF_STATE
