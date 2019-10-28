from threading import Thread
from time import sleep, time


class SensorDataUploader(Thread):
    def __init__(self, conn, fsm, interval):
        Thread.__init__(self)
        self.db = conn
        self.fsm = fsm
        self.interval = interval
        self.amount_processed = None
        self.timestamp = None

    def upload_data(self):
        firebase_data = self.fsm.get()
        amount_processed = 0
        for database in ['temperature', 'humidity', 'illumination', 'plant']:
            db_data = self.db.get(database, "uploaded = 0 order by id asc")
            if len(db_data) > 0:
                formatted_data = list(map(lambda id, value, status, timestamp, uploaded: { 'value': value, f"{'growth' if database == 'plant' else 'status'}": status, 'timestamp': timestamp }, *zip(*db_data)))
                for data in formatted_data:
                    if database == 'plant':
                        firebase_data[database].append(data)
                    else:
                        firebase_data[database]['values'].append(data)
                self.db.set(database, {'uploaded': 1}, "uploaded = 0")
                amount_processed += len(formatted_data)
        self.fsm.set(firebase_data)
        self.amount_processed = amount_processed
        self.timestamp = int(time())

    def log(self):
        print(f"[SensorDataUploader] Amount Processed: {self.amount_processed} - Timestamp: {self.timestamp}")

    def run(self):
        while True:
            self.upload_data()
            self.log()
            sleep(self.interval)
