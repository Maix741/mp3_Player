import random

from PySide6.QtCore import Signal, Slot, QThread


class PlaylistThread(QThread):
    """A QThread to play a list of media files."""
    song_changed: Signal = Signal(str)
    disable_progress_slider: Signal = Signal(bool)
    is_alive: bool = True
    is_paused: Signal = Signal(bool)
    is_looping: Signal = Signal(bool)
    rewinded: Signal = Signal(bool)

    def __init__(self, music_handler, media_files: list[str], shuffle: bool = False, parent=None) -> None:
        """Initialize the Playlist Thread.

        Args:
            media_files (list[str]): The list of media files to play.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)
        self.media_files = media_files
        self.music_handler = music_handler

        if shuffle:
            random.shuffle(self.media_files)
        self._is_paused = False
        self.is_paused.connect(self.update_paused_state)
        self.is_looping.connect(self.update_looping_state)

    @Slot(bool)
    def update_paused_state(self, paused: bool) -> None:
        """Update the paused state of the thread.

        Args:
            paused (bool): The new paused state.
        """
        self._is_paused = paused

    @Slot(bool)
    def update_rewind_state(self, rewinded: bool) -> None:
        """Update the paused state of the thread.

        Args:
            paused (bool): The new paused state.
        """
        self._rewinded = rewinded

    @Slot(bool)
    def update_looping_state(self, looping: bool) -> None:
        """Update the looping state of the thread.

        Args:
            looping (bool): The new looping state.
        """
        self._is_looping = looping

    def run(self) -> None:
        """Start playing the Playlist."""
        for media_file in self.media_files:
            if not self.is_alive: break

            self.music_handler.load_and_play(media_file)
            self.is_paused.emit(False)
            self.is_looping.emit(False)

            # Emit signal to update song on the GUI
            self.song_changed.emit(media_file)

            # Wait until the song is finished
            while (self.music_handler.is_playing() or self._is_paused or self._is_looping) and self.is_alive:
                if not self._is_paused and not self.music_handler.is_playing():
                    if self.is_looping:
                        self.music_handler.load_and_play(media_file)
                    else:
                        if self._rewinded:
                            self.media_files.reverse()
                            self._rewinded = False
                            break
                        self.music_handler.unpause()
                if not self._is_paused:
                    self.disable_progress_slider.emit(False)
                self.msleep(200)  # Sleep to avoid blocking the thread

        self.disable_progress_slider.emit(True)

    def terminate(self):
        """Terminate the Playlist Thread."""
        self.is_alive = False
        self.msleep(201)
        self.music_handler.stop_and_unload()
        self.song_changed.emit(None)

        return super().terminate()

    def stop(self):
        """Stop the Playlist Thread."""
        self.terminate()
