from pathlib import Path
import os, sys
import locale
import json


class SettingsHandler:
    def __init__(self,
                 initial_directory: str = "", locale: str = locale.getlocale()[0], shuffle : bool = False, load_saved: bool = True
                 ) -> None:
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


if __name__ == "__main__":
    handler: SettingsHandler = SettingsHandler()
    print(handler.settings)
