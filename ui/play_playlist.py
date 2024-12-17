from PySide6.QtCore import QThread, Signal
import pygame


class PlaylistThread(QThread):
    song_changed = Signal(str)

    def __init__(self, media_files: list[str], parent=None):
        super().__init__(parent)
        self.media_files = media_files

    def run(self):
        for media_file in self.media_files:
            pygame.mixer.music.load(media_file)
            pygame.mixer.music.play()

            # Emit signal to update song on the GUI
            self.song_changed.emit(media_file)

            # Wait until the song is finished
            while pygame.mixer.music.get_busy():
                self.msleep(100)  # Sleep to avoid blocking the thread
