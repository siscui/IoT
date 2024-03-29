from label_image import LabelImage
import datetime

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
        return None, 0

    def analyze(self, filename):
        self.filename = filename
        print("Analizando especie ...")
        t1 = datetime.datetime.now()
        self.species, percentage = self.detect_species()
        tot = datetime.datetime.now() - t1
        print(f"{round(tot.total_seconds(),1)} seg.")
        print(self.species)
        print("Detectar maduracion ...")
        t1 = datetime.datetime.now()
        label, maturity = self.detect_maturation()
        tot = datetime.datetime.now() - t1
        print(f"{round(tot.total_seconds(),1)} seg.")
        print(maturity)
        return self.species, percentage, 1 - maturity if label == 'no' else maturity
