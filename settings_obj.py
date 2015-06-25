import json

class Settings_interface():
    def __init__(self):
        self.load_file = "settings.json"
        try:
            with open(self.load_file) as jfile:
                self.settings = json.load(jfile)
        except FileNotFoundError as ferror:
            print ("Critical: Json settings file not found")
            raise ferror #probs doesnt work



