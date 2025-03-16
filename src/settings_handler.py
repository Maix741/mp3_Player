from pathlib import Path
import os, sys
import locale
import json


class SettingsHandler:
    def __init__(self,
                 initial_directory: str = "", locale: str = locale.getlocale()[0], shuffle : bool = False, load_saved: bool = True
                 ) -> None:
        
        self.tester: SettingsTester = SettingsTester()
        # Get the settings file path
        current_dir: str = os.path.dirname(sys.argv[0])
        if current_dir.endswith(("src", "bin")):
            self.settings_file: str = os.path.join(Path(current_dir).parent, "config", "settings.json")
        else: # Running from root directory
            self.settings_file: str = os.path.join(current_dir, "config", "settings.json")

        # Default settings
        self.initial_directory: str = initial_directory
        self.load_saved_playlist: bool = load_saved
        self.system_locale: str = locale
        self.shuffle: bool = shuffle
        self.volume: int = 50
        self.design: int = 0    # Literal[0, 1, 2] 0 -> system, 1 -> dark, 2 -> light

        self.load()

    def get(self, key: str) -> str | int | bool:
        return self.settings.get(key)

    def set(self, key: str, value: str | int | bool) -> None:
        self.settings[key] = value

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def load(self) -> None:
        try:
            with open(self.settings_file, "r") as file:
                self.settings: dict[str, str] = json.loads(file.read())

        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            self.settings: dict[str, str] = {}

        if self.settings:
            new_settings = self.tester.test_all_settings(self.settings)
            if new_settings != self.settings:
                self.settings = new_settings
                self.save()
            return

        self.settings: dict[str, str] = {
            "initial_directory": self.initial_directory,
            "system_locale": self.system_locale,
            "volume": 50,
            "shuffle": self.shuffle,
            "load_saved_playlist": self.load_saved_playlist,
            "design": self.design
        }
        self.save()


class SettingsTester:
    def __init__(self):
        self.settings: dict[str, str] = {
            "initial_directory": "",
            "system_locale": "en_US",
            "volume": 50,
            "shuffle": False,
            "load_saved_playlist": True,
            "design": 0
        }

    def test_all_settings(self, settings_to_test: dict[str, str | int | bool]) -> dict[str, str | int | bool]:
        try:
            if not list(settings_to_test.keys()).sort() == list(self.settings.keys()).sort():
                pass

            if not type(settings_to_test["initial_directory"]) == str:
                settings_to_test["initial_directory"] = self.settings["initial_directory"]
            if not type(settings_to_test["system_locale"]) == str:
                settings_to_test["system_locale"] = self.settings["system_locale"]
            if not type(settings_to_test["volume"]) == int:
                settings_to_test["volume"] = self.settings["volume"]
            if not type(settings_to_test["shuffle"]) == bool:
                settings_to_test["shuffle"] = self.settings["shuffle"]
            if not type(settings_to_test["load_saved_playlist"]) == bool:
                settings_to_test["load_saved_playlist"] = self.settings["load_saved_playlist"]
            if not type(settings_to_test["design"]) == int:
                settings_to_test["design"] = self.settings["design"]

            return settings_to_test
        except (KeyError, IndexError, ValueError): return self.settings


if __name__ == "__main__":
    handler: SettingsHandler = SettingsHandler()
    print(handler.settings)
