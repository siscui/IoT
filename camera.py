from picamera import PiCamera
from time import sleep, time


class Camera:
    def __init__(self):
        self.camera = PiCamera()

    def take_photo(self):
        filename = f"./photos/{int(time())}.jpg"
        with open(filename, 'wb') as file:
            self.camera.start_preview()
            sleep(0.5)
            self.camera.capture(file)
            self.camera.stop_preview()
        return filename
