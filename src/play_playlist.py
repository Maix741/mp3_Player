from PySide6.QtCore import Signal, Slot, QThread
import pygame


class PlaylistThread(QThread):
    """A QThread to play a list of media files."""
    song_changed: Signal = Signal(str)
    disable_progress_slider: Signal = Signal(bool)
    is_alive: bool = True
    is_paused: Signal = Signal(bool)

    def __init__(self, media_files: list[str], parent=None) -> None:
        """Initialize the Playlist Thread.

        Args:
            media_files (list[str]): The list of media files to play.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)
        self.media_files = media_files
        self._is_paused = False
        self.is_paused.connect(self.update_paused_state)

    @Slot(bool)
    def update_paused_state(self, paused: bool) -> None:
        """Update the paused state of the thread.

        Args:
            paused (bool): The new paused state.
        """
        self._is_paused = paused

    def run(self) -> None:
        """Start playing the Playlist."""
        for media_file in self.media_files:
            if not self.is_alive: break

            pygame.mixer.music.load(media_file)
            pygame.mixer.music.play()
            self.is_paused.emit(False)

            # Emit signal to update song on the GUI
            self.song_changed.emit(media_file)

            # Wait until the song is finished
            while (pygame.mixer.music.get_busy() and self.is_alive) or (self._is_paused and self.is_alive):
                if not self._is_paused and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.unpause()

                self.disable_progress_slider.emit(False)
                self.msleep(200)  # Sleep to avoid blocking the thread

        self.disable_progress_slider.emit(True)

    def terminate(self):
        """Terminate the Playlist Thread."""
        self.is_alive = False
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.song_changed.emit(None)
        self.msleep(100)
        return super().terminate()

    def stop(self):
        """Stop the Playlist Thread."""
        self.terminate()