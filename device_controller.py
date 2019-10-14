class PumpController:
    def __init__(self, pin):
        self.pin = pin
        self.conditions = []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def verify_conditions(self):
        for condition in self.conditions:
            

    def toggle(self, state):
        pass