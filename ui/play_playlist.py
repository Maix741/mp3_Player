from PySide6.QtCore import QThread, Signal
import pygame


class PlaylistThread(QThread):
    song_changed = Signal(str)
    hide_progress_slider = Signal(bool)
    is_alive = True

    def __init__(self, media_files: list[str], parent=None):
        super().__init__(parent)
        self.media_files = media_files

    def run(self):
        for media_file in self.media_files:
            if not self.is_alive: break

            pygame.mixer.music.load(media_file)
            pygame.mixer.music.play()

            # Emit signal to update song on the GUI
            self.song_changed.emit(media_file)

            # Wait until the song is finished
            while pygame.mixer.music.get_busy() and self.is_alive:
                self.hide_progress_slider.emit(False)
                self.msleep(100)  # Sleep to avoid blocking the thread

        self.hide_progress_slider.emit(True)
    
    def terminate(self):
        self.is_alive = False
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.song_changed.emit(None)
        self.msleep(100)
        return super().terminate()
    
    def stop(self):
        self.terminate()