from label_image import LabelImage


class AIModelManager:

    def __init__(self, image_path):
        self.image_path = image_path

    def detect_species(self):
        return LabelImage(model_file="models/detect_species_mobilenet_100_160.pb",
                          label_file="models/detect_species_mobilenet_100_160.txt",
                          filename=self.image_path).run()

    def detect_maturation(self, species):
        if species == 'tomate' or species == 'morron':
            return LabelImage(model_file=f"models/maturity_{species}_100_160.pb",
                              label_file=f"models/maturity_{species}_100_160.txt",
                              input_layer="Placeholder",
                              output_layer="final_result",
                              filename=self.image_path).run()
        return None, None

    def run(self):
        species, percentage = self.detect_species()
        _, maturation = self.detect_maturation(species)
        return species, percentage, maturation
