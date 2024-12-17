import sys, os

from PySide6.QtWidgets import QMainWindow, QPushButton, QSlider, QVBoxLayout, QListWidget, QFileDialog, QLabel, QMenu, QWidget, QSpacerItem, QSizePolicy, QDockWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
import pygame

if __name__ == "__main__":
    from play_playlist import PlaylistThread

else: from .play_playlist import PlaylistThread


class MP3_Player(QMainWindow):
    def __init__(self, initial_directory: str | None = None, load_saved: bool = True, parent = None):
        super().__init__(parent)

        self.setWindowTitle("MP3 Player")
        self.setGeometry(100, 100, 600, 400)

        # Initialize Pygame mixer
        pygame.mixer.init()

        # List to keep track of loaded media files
        self.media_files = []
        self.current_index = 0
        self.current_music = None
        self.music_length = 0
        self.audio_file_types = (".mp3", ".wav")
        self.initial_directory = initial_directory

        # Create UI elements
        self.init_gui()

        # Timer to update progress slider
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update progress every 100 ms


    def init_gui(self) -> None:
        # Create the central widget layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a main layout for the central widget
        central_layout = QVBoxLayout(central_widget)

        self.current_song = QLabel(f"Song: {self.current_music}", self)
        central_layout.addWidget(self.current_song)

        # Create and set up the playlist widget
        self.playlist_list = QListWidget(self)
        self.playlist_list.clicked.connect(self.play_selected)
        self.playlist_list.setFixedWidth(1000)  # Optional: Set a fixed width
        self.playlist_list.setFixedHeight(500)  # Optional: Set a fixed height
        central_layout.addWidget(self.playlist_list, alignment=Qt.AlignCenter)

        # Add a spacer to push elements down
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        central_layout.addSpacerItem(spacer_item)

        self.create_sliders(central_layout)

        # Create the dockable panel for the left side buttons
        self.create_controls_dock()

        # Create menu bar (handled by QMainWindow)
        self.create_menubar()

    def create_sliders(self, central_layout: QVBoxLayout) -> None:
        # Progress slider (for tracking and seeking audio progress)
        self.progress_slider = QSlider(Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderPressed.connect(self.seek_audio)
        self.progress_slider.setHidden(True)
        central_layout.addWidget(QLabel("Progress"))
        central_layout.addWidget(self.progress_slider)

        # Volume slider (bottom)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        central_layout.addWidget(QLabel("Volume"))
        central_layout.addWidget(self.volume_slider)

    def create_controls_dock(self) -> None:
        # Create a QWidget to house the left-side controls
        dock_widget = QDockWidget("Controls", self)
        dock_widget.setFeatures(QDockWidget.DockWidgetMovable)

        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget(self)
        dock_layout = QVBoxLayout(dock_content)

        # Spacer to keep buttons at the bottom
        dock_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Play / Pause button
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        dock_layout.addWidget(self.play_button)

        self.play_playlist_button = QPushButton("Play Playlist", self)
        self.play_playlist_button.clicked.connect(self.play_playlist)
        dock_layout.addWidget(self.play_playlist_button)

        # Stop button
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_audio)
        dock_layout.addWidget(self.stop_button)

        # Playlist button
        self.playlist_button = QPushButton("Add from Folder", self)
        self.playlist_button.clicked.connect(self.load_playlist_folder)
        dock_layout.addWidget(self.playlist_button)

        dock_widget.setWidget(dock_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

    def remove_audio_from_playlist(self):
        index = self.playlist_list.row(self.playlist_list.currentItem())
        self.playlist_list.takeItem(index)
        self.media_files.pop(index)

    def contextMenuEvent(self, event) -> None:
        # Create the context menu
        context_menu = QMenu(self)

        # Add actions to the context menu
        action_play = QAction("play", self)
        action_remove = QAction("remove", self)

        # Connect actions to slots (optional)
        action_play.triggered.connect(self.play_selected)
        action_remove.triggered.connect(self.remove_audio_from_playlist)

        # Add actions to the context menu
        context_menu.addAction(action_play)
        context_menu.addAction(action_remove)

        # Show the context menu at the mouse position
        context_menu.exec(event.globalPos())

    def create_menubar(self) -> None:
        # Create the menu bar
        menubar = self.menuBar()

        # Create "File" menu
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)

        # Add actions to the "File" menu
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_single_files)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def play_playlist(self) -> None:
        if self.play_playlist_button.text() == "Stop Playlist":
            self.on_playlist_finished()

        # Create and start the playlist thread
        self.playlist_thread = PlaylistThread(self.media_files)
        self.playlist_thread.song_changed.connect(self.update_current_song)
        self.playlist_thread.hide_progress_slider.connect(self.progress_slider.setHidden)
        self.playlist_thread.finished.connect(self.on_playlist_finished)

        self.play_playlist_button.setText("Stop Playlist")

        self.playlist_thread.start()

    def update_current_song(self, song: str) -> None:
        self.current_song.setText(f"Song: {self.current_music}")

    def on_playlist_finished(self) -> None:
        self.playlist_thread.stop()

        self.play_playlist_button.setText("Play Playlist")
        self.play_button.setText("Play")

        self.progress_slider.setHidden(True)
        self.progress_slider.setHidden(True)

    def toggle_play_pause(self) -> None:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_button.setText("Play")
            return

        if self.current_index == 0:  # If no track is selected, play the first one
            self.play_next()
        else:
            self.progress_slider.setHidden(False)
            pygame.mixer.music.unpause()

        self.play_button.setText("Pause")

    def stop_audio(self) -> None:
        self.progress_slider.setHidden(True)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.play_button.setText("Play")

    def set_volume(self, value) -> None:
        pygame.mixer.music.set_volume(value / 100)

    def load_playlist_folder(self, clear: bool = True) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Choose Playlist", self.initial_directory)

        if not directory: return

        files: list[str] = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(self.audio_file_types)]
        if clear:
            self.playlist_list.clear()  # Clear the playlist display
            self.media_files.clear()  # Clear the playlist

        self.media_files.extend(files) # Add the selected songs to the playlist

        self.playlist_list.addItems([os.path.basename(file) for file in files]) # Display the Songnames in the playlist

    def load_single_files(self, clear: bool = False) -> None:
        # Open file dialog to select MP3 files
        files, _ = QFileDialog.getOpenFileNames(self, "Select MP3 Files", "", self.audio_file_types[0])

        if not files: return

        if clear:
            self.playlist_list.clear()  # Clear the playlist display
            self.media_files.clear()  # Clear the playlist

        self.media_files.extend(files) # Add the selected songs to the playlist

        self.playlist_list.addItems([os.path.basename(file) for file in files]) # Display the Songnames in the playlist

    def play_selected(self) -> None:
        # Play the selected item in the playlist
        current_item = self.playlist_list.currentItem()
        if current_item:
            self.current_index = self.playlist_list.row(current_item)
            self.play_next()

    def play_next(self, media_file: str | None = None) -> None:
        # Check if there are any files in the playlist
        if not self.media_files:
            return

        self.progress_slider.setHidden(False)
        if not media_file:
            self.current_music = self.media_files[self.current_index]
        else: self.current_music = media_file

        self.current_song.setText(f"Song: {self.current_music}")
        pygame.mixer.music.load(self.current_music)
        pygame.mixer.music.play()

        # Get the length of the music in seconds and set the slider's range
        self.music_length = pygame.mixer.Sound(self.current_music).get_length()
        self.progress_slider.setRange(0, int(self.music_length))

    def update_progress(self) -> None:
        if pygame.mixer.music.get_busy():
            # Get current position of the audio file and update the slider
            current_position = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
            self.progress_slider.setValue(int(current_position))

    def seek_audio(self) -> None:
        # When the user clicks on the slider, move the audio to the selected position
        seek_position = self.progress_slider.value()
        pygame.mixer.music.set_pos(seek_position)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    player = MP3_Player(r"C:\Users\maxi2\Music\Stupendium")
    player.show()
    sys.exit(app.exec())
