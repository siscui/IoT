from threading import Thread
from time import sleep


class SensorDataUploader(Thread):
    def __init__(self, conn, fsm, interval):
        Thread.__init__(self)
        self.db = conn
        self.fsm = fsm
        self.interval = interval

    def upload_data(self):
        pass

    def run(self):
        self.upload_data()
        sleep(self.interval)
