import platform
import sys, os
import locale

from PySide6.QtWidgets import QApplication

from src import Mp3Player


if __name__ == "__main__":
    if platform.system() == "Windows":
        initial_directory: str = os.path.join(os.environ.get("USERPROFILE", ""), "Music")
        system_locale: str = locale.getlocale()[0]
    else:
        initial_directory: str = os.path.expanduser("~/Music")
        system_locale: str = "en_US"

    app: QApplication = QApplication(sys.argv)
    player: Mp3Player = Mp3Player(initial_directory, locale=system_locale)
    player.show()
    sys.exit(app.exec())
