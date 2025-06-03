import locale
import sys

from PySide6.QtWidgets import QApplication

from src import Mp3Player, get_music_directory


if __name__ == "__main__":
    system_locale: str = locale.getlocale()[0]
    initial_directory: str = get_music_directory()

    app: QApplication = QApplication(sys.argv)
    player: Mp3Player = Mp3Player(initial_directory, locale=system_locale)
    player.show()
    sys.exit(app.exec())
