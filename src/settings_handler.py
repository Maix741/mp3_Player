from pathlib import Path
import os, sys
import locale
import json


class SettingsHandler:
    def __init__(self) -> None:
        current_dir = os.path.dirname(sys.argv[0])
        if current_dir.endswith(("src", "bin")):
            self.settings_file = os.path.join(Path(current_dir).parent, "config", "settings.json")
        else: # Running from root directory
            self.settings_file = os.path.join(current_dir, "config", "settings.json")

        self.load()


    def get(self, key: str) -> str | int | bool:
        return self.settings.get(key)

    def set(self, key: str, value: str |int | bool) -> None:
        self.settings[key] = value

    def save(self):
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def load(self):
        try:
            with open(self.settings_file, "r") as file:
                self.settings: dict[str, str] = json.loads(file.read())

        except FileNotFoundError:
            self.settings: dict[str, str] = {}

        if self.settings:
            return

        self.settings: dict[str, str] = {
            "initial_directory": "",
            "system_locale": locale.getlocale()[0],
            "volume": 50,
            "shuffle": False,
            "load_saved_playlist": True
        }
        self.save()


if __name__ == "__main__":
    handler = SettingsHandler()
    print(handler.settings)
