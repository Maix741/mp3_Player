import sys

from PySide6.QtWidgets import QApplication

from ui import *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MP3_Player(r"C:\Users\maxi2\Music\Stupendium")
    player.show()
    sys.exit(app.exec())
