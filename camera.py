from picamera import PiCamera
from datetime import datetime
from time import sleep


class Camera:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.rotation = 180

    def take_photo(self):
        filename = f"./photos/{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        with open(filename, 'wb') as file:
            self.camera.start_preview()
            sleep(0.5)
            self.camera.capture(file)
            self.camera.stop_preview()
        return filename
