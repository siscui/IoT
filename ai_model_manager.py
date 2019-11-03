from label_image import LabelImage


class AIModelManager:

    def __init__(self):
        self.filename = None
        self.species = None

    def detect_species(self):
        return LabelImage(model_file="models/detect_species_mobilenet_100_160.pb",
                          label_file="models/detect_species_mobilenet_100_160.txt",
                          filename=self.filename).run()

    def detect_maturation(self):
        if self.species == 'tomate' or self.species == 'morron':
            return LabelImage(model_file=f"models/maturity_{self.species}_100_160.pb",
                              label_file=f"models/maturity_{self.species}_100_160.txt",
                              input_layer="Placeholder",
                              output_layer="final_result",
                              filename=self.filename).run()
        return None, None

    def analyze(self, filename):
        self.filename = filename
        self.species, percentage = self.detect_species()
        _, maturity = self.detect_maturation()
        return self.species, percentage, maturity
