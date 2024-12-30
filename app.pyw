import sys

from PySide6.QtWidgets import QApplication

from src import *


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    player: MP3_Player = MP3_Player(os.path.join(os.environ['USERPROFILE'], 'Music'))
    player.show()
    sys.exit(app.exec())
