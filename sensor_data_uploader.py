from time import time


class SensorDataUploader:
    def __init__(self, conn, fsm):
        self.db = conn
        self.fsm = fsm
        self.amount_processed = None
        self.timestamp = None
        self.updated = False

    def upload_data(self, lamp_state, heater_state, pump_state):
        firebase_data = self.fsm.get()
        amount_processed = 0
        for database in ['temperature', 'humidity', 'illumination', 'plant']:
            db_data = self.db.get(database, "uploaded = 0 order by id asc")
            if len(db_data) > 0:
                formatted_data = list(map(lambda _id, value, status, timestamp, uploaded: {
                                                            'value': value,
                                                            f"{'growth' if database == 'plant' else 'status'}": status,
                                                            'timestamp': timestamp}, *zip(*db_data)))
                for data in formatted_data:
                    if database == 'plant':
                        firebase_data[database].append(data)
                    else:
                        firebase_data[database]['values'].append(data)
                self.db.set(database, {'uploaded': 1}, "uploaded = 0")
                amount_processed += len(formatted_data)
            else:
                print("No hay lecturas para subir.")
        firebase_data['lamp']['state'] = lamp_state
        firebase_data['heater']['state'] = heater_state
        firebase_data['pump']['state'] = pump_state
        self.fsm.set(firebase_data)
        self.amount_processed = amount_processed
        self.timestamp = int(time())

    def is_updated(self):
        return self.updated

    def set_updated(self, value):
        self.updated = value

    def log(self):
        print(f"[SensorDataUploader] Amount Processed: {self.amount_processed} - Timestamp: {self.timestamp}")

    def run(self, lamp_state, heater_state, pump_state):
        self.upload_data(lamp_state, heater_state, pump_state)
        self.log()
        self.updated = True
