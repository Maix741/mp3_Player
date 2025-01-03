import sys, platform

from PySide6.QtWidgets import QApplication

from src import *


if __name__ == "__main__":
    if platform.system() == "Windows":
        initial_directory = os.path.join(os.environ['USERPROFILE'], 'Music')
    else: initial_directory = None

    app: QApplication = QApplication(sys.argv)
    player: MP3_Player = MP3_Player(initial_directory)
    player.show()
    sys.exit(app.exec())
