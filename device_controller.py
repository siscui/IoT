class DeviceController:
    def __init__(self, pin):
        self.pin = pin
        self.conditions = []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def verify_conditions(self, value, c_type):
        for condition in self.conditions:
            if condition(value, c_type):
                return self.set_state(1)
        self.set_state(0)

    def get_state(self):
        pass

    def set_state(self, state):
        pass
