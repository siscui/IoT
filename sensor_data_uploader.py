from threading import Thread
from time import sleep


class SensorDataUploader(Thread):
    def __init__(self, conn, fsm, interval):
        Thread.__init__(self)
        self.db = conn
        self.fsm = fsm
        self.interval = interval

    def upload_data(self):
        firebase_data = self.fsm.get()
        for database in ['temperature', 'humidity', 'illumination', 'plant']:
            db_data = self.db.get(database, "uploaded = 0 order by id asc")
            formatted_data = list(map(lambda _, value, status, time: {
                'value': value, 'status': status, 'time': time
            }, *zip(*db_data)))
            for data in formatted_data:
                firebase_data[database].values.push(data)
            self.db.set(database, {'uploaded': 1}, "uploaded = 0")
        self.fsm.set(firebase_data)

    def run(self):
        self.upload_data()
        sleep(self.interval)
