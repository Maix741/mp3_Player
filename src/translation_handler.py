from pathlib import Path
import os, sys

from PySide6.QtCore import QTranslator, QCoreApplication

if __name__ == "__main__":
    from settings_handler import SettingsHandler


class TranslationHandler:
    def __init__(self, settings_handler, translator) -> None:
        self.settings_handler = settings_handler
        self.translator = translator
        self.select_locale()
        self.load_locale()

    def select_locale(self):
        self.locale = self.settings_handler.get("system_locale")

    def load_locale(self) -> None:
        # Load translations
        self.translator: QTranslator = QTranslator()
        current_path = os.path.dirname(sys.argv[0])
        if current_path.endswith(("bin", "src")):
            locales_folder = os.path.join((Path(current_path).parent), "locales")
        else: locales_folder = os.path.join(current_path, "locales")

        translation_file: str = os.path.join(locales_folder, f"{self.locale}.qm")
        if self.translator.load(translation_file):
            QCoreApplication.installTranslator(self.translator)


if __name__ == "__main__":
    handler = TranslationHandler()
    print(handler.translator)