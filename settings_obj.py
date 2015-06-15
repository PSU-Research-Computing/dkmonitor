import json

class Settings_interface(self):
    def __init__(self):
        self.load_file = "settings.json"
        with json_genrator() as jfile:
            self.settings = json.load(jfile)

    def json_genrator(self):
        try:
            with open(self.load_file) as jfile:
                yield jfile
        except FileNotFoundError as ferror:
            print ("Critical: Json settings file not found")
            raise ferror #probs doesnt work


