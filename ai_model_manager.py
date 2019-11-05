from label_image import LabelImage


class AIModelManager:

    def __init__(self):
        self.filename = None
        self.species = None

    def detect_species(self):
        return LabelImage(model_file="models/detect_species.pb",
                          label_file="models/detect_species.txt",
                          input_layer="input",
                          output_layer="final_result",
                          input_height=160,
                          input_width=160,
                          filename=self.filename).run()

    def detect_maturation(self):
        if self.species == 'tomate' or self.species == 'morron':
            return LabelImage(model_file=f"models/maturity_{self.species}.pb",
                              label_file=f"models/maturity_{self.species}.txt",
                              input_layer="input",
                              output_layer="final_result",
                              input_width=160,
                              input_height=160,
                              filename=self.filename).run()
        return None, None

    def analyze(self, filename):
        self.filename = filename
        self.species, percentage = self.detect_species()
        _, maturity = self.detect_maturation()
        return self.species, percentage, maturity
