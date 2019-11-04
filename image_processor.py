from ai_model_manager import AIModelManager
from camera import Camera


class ImageProcessor:
    def __init__(self, conn):
        self.conn = conn
        self.ai = AIModelManager()
        self.camera = Camera()
        self.last_photo = None
        self.species = None
        self.percentage = None
        self.maturity = None
        self.timestamp = None

    def take_photo(self):
        self.last_photo = self.camera.take_photo()

    def analyze_photo(self):
        self.species, self.percentage, self.maturity = self.ai.analyze(self.last_photo)

    def save(self):
        self.timestamp = self.conn.save('PLANT', {'species': self.species, 'maturity': self.maturity})

    def log(self):
        print(f"[ImageProcessor] Plant: {self.species} - Percentage: {self.percentage} - Maturity: {self.maturity} - "
              f"Timestamp: {self.timestamp}")

    def run(self):
        self.take_photo()
        self.analyze_photo()
        self.save()
        self.log()
        return self.species, self.percentage, self.maturity
