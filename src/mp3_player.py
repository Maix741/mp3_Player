from pathlib import Path
import os, sys

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QSlider, QVBoxLayout, QListWidget, QFileDialog, QLabel, QMenu, QWidget, 
    QSpacerItem, QSizePolicy, QDockWidget, QScrollArea, QInputDialog, QHBoxLayout,
)
from PySide6.QtCore import QTranslator, QCoreApplication
from PySide6.QtGui import QAction, QContextMenuEvent, QIcon
from PySide6.QtCore import Qt, QTimer
from functools import partial
import pygame

if __name__ == "__main__":
    from play_playlist import PlaylistThread
    from load_playlists import SavedPlaylistsHandler
    from translation_handler import TranslationHandler
    from settings_handler import SettingsHandler
    from settings_gui import SettingsGUI

else:
    from .play_playlist import PlaylistThread
    from .load_playlists import SavedPlaylistsHandler
    from .translation_handler import TranslationHandler
    from .settings_handler import SettingsHandler
    from .settings_gui import SettingsGUI


class Mp3Player(QMainWindow):
    """A simple MP3 player application using Pygame and PySide6."""
    def __init__(self,
                 initial_directory: str | None = None, load_saved: bool = True, shuffle: bool = False, locale: str = "en_US",
                 parent: QWidget | None = None) -> None:
        """Initialize the MP3 Player.

        Args:
            initial_directory (str, optional): The initial directory to load files from. Defaults to None.
            load_saved (bool, optional): Whether to load saved playlists. Defaults to True.
            parent ([type], optional): The parent object. Defaults to None.
        """
        super().__init__(parent)
        # Initialize the settings handler
        self.settings_handler = SettingsHandler()

        # Set the system locale
        self.translator: QTranslator = QTranslator()
        self.translation_handler = TranslationHandler(self.settings_handler, self.translator)
        QCoreApplication.installTranslator(self.translator)

        # Set the window title and geometry
        self.setWindowTitle(self.tr("MP3 Player"))
        self.setGeometry(100, 100, 1000, 600)
        self.light_mode: bool = self.palette().color(self.backgroundRole()).lightness() > 128

        # Set the assets path based on current path
        current_path = os.path.dirname(sys.argv[0])
        if current_path.endswith(("bin", "src")):
            self.assets_path: str = os.path.join((Path(current_path).parent), "assets")
        else: self.assets_path: str = os.path.join(current_path, "assets")

        # Initialize Pygame mixer
        pygame.mixer.init()
        self.start_value: int = 0

        # Initialize variables
        self.audio_file_types: tuple[str] = (".mp3", ".wav", ".ogg", ".flac")
        self.media_files: list[str] = [] # List to keep track of loaded media files
        self.current_music: str | None = None
        self.current_index: int = 0
        self.music_length: int = 0
        self.max_previously_saved: int = 10
        self.previously_played: list[str] = [] # FIXME: currently useless
        self.is_looping: bool = False

        self.initial_directory: str | None = self.settings_handler.get("initial_directory") or initial_directory
        self.shuffle: bool = self.settings_handler.get("shuffle") or shuffle
        load_saved = self.settings_handler.get("load_saved_playlist")

        # Initialize the playlist loader
        self.loader: SavedPlaylistsHandler = SavedPlaylistsHandler()
        self.playlist_thread: PlaylistThread | None = None

        # Load existing playlists
        if load_saved:
            self.load_existing_playlists()
        else: self.existing_playlists = {}

        # Create UI elements
        self.init_gui()

        # Timer to update progress slider
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update progress every 100 ms

    def init_gui(self) -> None:
        """Initialize the GUI elements."""        
        # Set the window icon based on the system's color scheme
        if self.light_mode:
            self.setWindowIcon(QIcon(os.path.join(self.assets_path, "dark", "icon.png")))
        else:
            self.setWindowIcon(QIcon(os.path.join(self.assets_path, "light", "icon.png")))

        # Create the central widget layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a main layout for the central widget
        central_layout = QVBoxLayout(central_widget)

        self.current_song = QLabel(self.tr(f"Song: {self.current_music}"), self)

        # Set the font size using QFont
        font = self.current_song.font()
        font.setPointSize(20)  # Set the font size to 20
        self.current_song.setFont(font)

        central_layout.addWidget(self.current_song)

        # Create and set up the playlist widget
        self.playlist_list = QListWidget(self)
        self.playlist_list.clicked.connect(self.play_selected)

        # Allow the playlist to expand to fill the available space
        central_layout.addWidget(self.playlist_list)

        # Set the layout to stretch to fill available space
        central_layout.setStretch(1, 1)  # Make the playlist widget expand

        # Add a spacer to push elements down
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        central_layout.addSpacerItem(spacer_item)

        self.create_sliders(central_layout)

        # Create the dockable panel for the left side buttons
        self.create_controls_dock()

        # Create menu bar (handled by QMainWindow)
        self.create_menubar()

    def create_sliders(self, central_layout: QVBoxLayout) -> None:
        """Create the progress and volume sliders."""        
        # Create a layout for the progress slider and buttons
        progress_layout = QVBoxLayout()

        # Create a horizontal layout for the progress slider and buttons
        slider_layout = QHBoxLayout()

        # Rewind button
        self.rewind_button = QPushButton(self)
        self.rewind_button.setFixedWidth(40)  # Set a smaller width for the button
        if self.light_mode:
            self.rewind_button.setIcon(QIcon(os.path.join(self.assets_path, "dark", "rewind.png")))
        else:
            self.rewind_button.setIcon(QIcon(os.path.join(self.assets_path, "light", "rewind.png")))
        self.rewind_button.clicked.connect(self.rewind_song)
        slider_layout.addWidget(self.rewind_button)

        # Progress slider (for tracking and seeking audio progress)
        self.progress_slider = QSlider(Qt.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderPressed.connect(self.seek_audio)
        self.progress_slider.setDisabled(True)
        slider_layout.addWidget(self.progress_slider)

        # Skip button
        self.skip_button = QPushButton(self)
        self.skip_button.setFixedWidth(40)  # Set a smaller width for the button
        if self.light_mode:
            self.skip_button.setIcon(QIcon(os.path.join(self.assets_path, "dark", "skip.png")))
        else:
            self.skip_button.setIcon(QIcon(os.path.join(self.assets_path, "light", "skip.png")))
        self.skip_button.clicked.connect(self.skip_song)
        slider_layout.addWidget(self.skip_button)

        # Add the slider layout to the progress layout
        progress_layout.addLayout(slider_layout)

        self.skip_button.clicked.connect(self.play_next)
        progress_layout.addWidget(self.skip_button)

        # Add the progress layout to the central layout
        central_layout.addLayout(progress_layout)

        # Volume slider (bottom)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.settings_handler.get("volume") or 50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        central_layout.addWidget(QLabel(self.tr("Volume")))
        central_layout.addWidget(self.volume_slider)

    def create_controls_dock(self) -> None:
        """Create the dock widget with control buttons."""        
        """Recreate the entire dock widget with updated content."""
        # Remove the previous dock widget if it exists
        if hasattr(self, "dock_widget"):
            self.removeDockWidget(self.dock_widget)
            del self.dock_widget

        # Create a new dock widget
        self.dock_widget = QDockWidget(self.tr("Controls"), self)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget(self)
        dock_layout = QVBoxLayout(dock_content)

        # Create buttons for all saved playlists if any
        if self.existing_playlists:
            self.create_saved_playlists_button(dock_layout)

        # Spacer to keep buttons at the bottom if no playlists exist
        if not self.existing_playlists:
            dock_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Play / Pause button
        self.play_button = QPushButton(self.tr("Play"), self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        dock_layout.addWidget(self.play_button)

        self.play_playlist_button = QPushButton(self.tr("Play Playlist"), self)
        self.play_playlist_button.clicked.connect(self.play_playlist)
        dock_layout.addWidget(self.play_playlist_button)

        # Stop button
        self.stop_button = QPushButton(self.tr("Stop"), self)
        self.stop_button.clicked.connect(self.stop_audio)
        dock_layout.addWidget(self.stop_button)

        # loop button
        self.loop_button = QPushButton(self.tr("Loop"), self)
        self.loop_button.clicked.connect(self.loop_song) # TODO
        dock_layout.addWidget(self.loop_button)

        # Save Playlist button
        self.save_playlist_button = QPushButton(self.tr("Save Playlist"), self)
        self.save_playlist_button.clicked.connect(self.save_playlist)
        dock_layout.addWidget(self.save_playlist_button)

        # Playlist button
        self.playlist_button = QPushButton(self.tr("Add from Folder"), self)
        self.playlist_button.clicked.connect(lambda: self.load_playlist_folder(False))
        dock_layout.addWidget(self.playlist_button)

        self.dock_widget.setWidget(dock_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

    def create_saved_playlists_button(self, dock_layout: QVBoxLayout) -> None:
        """Create buttons for each saved playlist."""        
        # Create a QScrollArea to make the list scrollable (only once)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(button_container)

        # Add the scroll area to the dock layout
        dock_layout.addWidget(scroll_area)

        # Add new buttons based on the updated playlists
        for name in self.existing_playlists.keys():
            playlist_button = QPushButton(name, self)
            playlist_button.clicked.connect(partial(self.load_playlist, name))
            playlist_button.setContextMenuPolicy(Qt.CustomContextMenu)
            playlist_button.customContextMenuRequested.connect(partial(self.show_playlist_context_menu, name, playlist_button))
            button_layout.addWidget(playlist_button)

        # Add a spacer to ensure buttons stay at the top if there is extra space
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.addSpacerItem(spacer)

    def show_playlist_context_menu(self, playlist_name: str, playlist_button: QPushButton, position) -> None:
        """Show context menu for the saved playlists."""        
        context_menu = QMenu(self)

        delete_action = QAction(self.tr("Delete"), self)
        delete_action.triggered.connect(partial(self.delete_playlist, playlist_name))

        context_menu.addAction(delete_action)
        global_position = playlist_button.mapToGlobal(position)
        context_menu.exec(global_position)

    def delete_playlist(self, playlist_name: str) -> None:
        """Delete the selected playlist."""        
        self.loader.delete_playlist(playlist_name)
        self.load_existing_playlists()
        self.reload_dock_widget()

    def reload_dock_widget(self) -> None:
        """Reload the entire dock widget to reflect changes in existing playlists."""        
        self.create_controls_dock()

    def remove_audio_from_playlist(self) -> None:
        """Remove the selected audio file from the playlist."""
        if not self.media_files: return
        # remove from programm and GUI
        index = self.playlist_list.row(self.playlist_list.currentItem())
        self.playlist_list.takeItem(index)
        song_path = self.media_files.pop(index)

        # remove from saved playlist
        if not self.existing_playlists:
            return
        for playlist, name in zip(self.existing_playlists.values(), self.existing_playlists.keys()):
            if song_path in playlist:
                self.loader.remove_from_playlist(name, self.current_music)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Create a context menu for the playlist."""        
        # Check if the event position is within the playlist area
        if self.playlist_list.geometry().contains(event.pos()):
            # Create the context menu
            context_menu = QMenu(self)

            # Add actions to the context menu
            action_play = QAction(self.tr("Play"), self)
            action_remove = QAction(self.tr("Remove"), self)
            action_add_to_playlist = QAction(self.tr("Add to playlist"), self)

            # Connect actions to slots (optional)
            action_play.triggered.connect(self.play_selected)
            action_remove.triggered.connect(self.remove_audio_from_playlist)
            action_add_to_playlist.triggered.connect(self.add_to_playlist)

            # Add actions to the context menu
            context_menu.addAction(action_play)
            context_menu.addAction(action_remove)
            context_menu.addAction(action_add_to_playlist)

            # Show the context menu at the mouse position
            context_menu.exec(event.globalPos())

    def create_menubar(self) -> None:
        """Create the menu bar with file and settings actions."""        
        def show_settings() -> None:
            """Show the settings window."""
            if self.settings_window is None:
                self.settings_window = SettingsGUI(self.settings_handler, self.translator)
                self.settings_window.setWindowModality(Qt.ApplicationModal)
                self.settings_window.show()

        # Create the menu bar
        menubar = self.menuBar()

        # Create "File" menu
        file_menu = QMenu(self.tr("File"), self)
        menubar.addMenu(file_menu)

        # Add actions to the "File" menu
        open_action = QAction(self.tr("Open"), self)
        open_action.triggered.connect(self.load_single_files)
        file_menu.addAction(open_action)

        exit_action = QAction(self.tr("Exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        clear_action = QAction(self.tr("Clear"), self)
        clear_action.triggered.connect(self.clear_playlist)
        file_menu.addAction(clear_action)

        # Create "Prefrences" menu
        Prefrences_menu = QMenu(self.tr("Prefrences"), self)
        menubar.addMenu(Prefrences_menu)

        # Add actions to the "Settings" menu
        settings_action = QAction(self.tr("Settings"), self)
        self.settings_window = None
        settings_action.triggered.connect(show_settings)


        Prefrences_menu.addAction(settings_action)
 
    def clear_playlist(self) -> None:
            """Clear the playlist and stop the current audio."""            
            self.playlist_list.clear()  # Clear the playlist display
            self.media_files.clear()  # Clear the playlist

            self.current_index = 0
            self.current_music = None
            self.update_current_song()

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def play_playlist(self) -> None:
        """Play the entire playlist."""        
        if self.play_playlist_button.text() == self.tr("Stop Playlist"):
            self.on_playlist_finished()

        # Create and start the playlist thread
        self.playlist_thread = PlaylistThread(self.media_files, self.shuffle)

        self.playlist_thread.is_paused.emit(False)
        self.playlist_thread.is_looping.emit(self.is_looping)
        self.playlist_thread.song_changed.connect(self.update_current_song)
        self.playlist_thread.disable_progress_slider.connect(self.progress_slider.setDisabled)
        self.playlist_thread.finished.connect(self.on_playlist_finished)

        self.play_playlist_button.setText(self.tr("Stop Playlist"))
        self.play_button.setText(self.tr("Pause"))

        self.playlist_thread.start()

    def update_current_song(self, song: str | None = None) -> None:
        """Update the current song label with the provided song name."""        
        max_length = 50  # Define the maximum length for the song name

        if song:
            self.previously_played.append(song)
            display_name = os.path.basename(song)
        elif self.current_music:
            self.previously_played.append(self.current_music)
            display_name = os.path.basename(self.current_music)
        else:
            display_name = self.tr("None")

        if len(self.previously_played) > self.max_previously_saved:
            self.previously_played = self.previously_played[-self.max_previously_saved:]

        if len(display_name) > max_length:
            display_name = display_name[:max_length] + "..."

        self.current_song.setText(self.tr(f"Song: {display_name}"))

    def on_playlist_finished(self) -> None:
        """Stop the playlist and reset the buttons."""        
        self.playlist_thread.stop()

        self.play_playlist_button.setText(self.tr("Play Playlist"))
        self.play_button.setText(self.tr("Play"))

        self.progress_slider.setDisabled(True)
        self.progress_slider.setDisabled(True)

    def toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""        
        if pygame.mixer.music.get_busy():
            if self.playlist_thread:
                self.playlist_thread.is_paused.emit(True)

            pygame.mixer.music.pause()
            is_paused: bool = True
            self.play_button.setText(self.tr("Play"))
            return

        else:
            self.progress_slider.setDisabled(False)
            pygame.mixer.music.unpause()
            if self.playlist_thread:
                self.playlist_thread.is_paused.emit(False)
            is_paused: bool = False
            self.play_button.setText(self.tr("Pause"))

        if not self.playlist_thread and not pygame.mixer.music.get_busy() and not is_paused:  # If no track is playing, play the first one
            self.play_next()

    def skip_song(self) -> None:
        """Skip to the next song in the playlist."""        
        if self.shuffle:
            self.current_index = (self.current_index + 1) % len(self.media_files)
        else:
            self.current_index = (self.current_index + 1) % len(self.media_files)
        self.play_next()

    def loop_song(self) -> None:
        """Toggle looping of the current song."""        
        if not pygame.mixer.music.get_busy():
            return

        if pygame.mixer.music.get_endevent() == pygame.USEREVENT:
            pygame.mixer.music.set_endevent()
            self.is_looping = False
            if self.playlist_thread:
                self.playlist_thread.is_looping.emit(self.is_looping)

            self.loop_button.setText(self.tr("Loop"))

        else:
            self.is_looping = True
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            if self.playlist_thread:
                self.playlist_thread.is_looping.emit(self.is_looping)

            self.loop_button.setText(self.tr("Unloop"))

    def rewind_song(self) -> None:
        """Rewind to the previous song in the playlist."""        
        if self.shuffle:
            self.current_index = (self.current_index - 1) % len(self.media_files)
        else:
            self.current_index = (self.current_index - 1) % len(self.media_files)
        self.play_next()

    def stop_audio(self) -> None:
        """Stop the current audio and reset the buttons."""        
        self.progress_slider.setDisabled(True)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        if not self.playlist_thread: # If a playlist is playing, don't reset the play button
            self.play_button.setText(self.tr("Play"))
            self.progress_slider.setValue(0)

    def set_volume(self, value: float) -> None:
        """Set the volume of the audio."""        
        pygame.mixer.music.set_volume(value / 100)

    def load_playlist_folder(self, clear: bool = True) -> None:
        """Load all audio files from a selected folder."""        
        directory = QFileDialog.getExistingDirectory(self, self.tr("Choose Playlist"), self.initial_directory)

        if not directory: return

        files: list[str] = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(self.audio_file_types)]
        if clear:
            self.clear_playlist()
        self.media_files.extend(files) # Add the selected songs to the playlist

        self.playlist_list.addItems([os.path.basename(file) for file in files]) # Display the Songnames in the playlist

    def load_playlist(self, name: str) -> None:
        """Load an existing playlist."""        
        self.playlist_list.clear()
        self.playlist_list.addItems([os.path.basename(file) for file in self.existing_playlists[name]]) # Display the Songnames in the playlist in the widget
        self.media_files = self.existing_playlists[name]

    def load_existing_playlists(self) -> None:
        """Load the existing playlists."""        
        self.existing_playlists: dict[str, list[str]] = self.loader.load_playlists()

    def save_playlist(self) -> None:
        """Save the current playlist."""        
        # Create a dialog that asks the user for their name
        playlist_name, ok = QInputDialog.getText(self, self.tr("Enter Name"), self.tr("Please enter the name of the Playlist:"))

        if ok and playlist_name:
            # Show the name in a message box if it's provided
            self.loader.save_playlist(playlist_name, self.media_files)

        self.load_existing_playlists()
        self.reload_dock_widget()

    def add_to_playlist(self) -> None:
        """Add the selected audio file to a playlist."""        
        current_item = self.playlist_list.currentItem()
        if not current_item:
            return
        playlist_name, ok = QInputDialog.getText(self, self.tr("Enter Playlist Name"), self.tr("Please enter the name of the Playlist:"))
        if not ok or not playlist_name:
            return
        self.loader.add_to_playlist(playlist_name, self.media_files[self.playlist_list.row(current_item)])
        self.load_existing_playlists()
        self.reload_dock_widget()

    def load_single_files(self, clear: bool = False) -> None:
        """Load single audio files."""        
        # Open file dialog to select MP3 files
        files, _ = QFileDialog.getOpenFileNames(self,
                                                self.tr("Select MP3 Files"),
                                                self.initial_directory,
                                                self.tr("audio (*.mp3 *.wav *.ogg *.flac);;All Files (*)"))

        if not files: return

        if clear:
            self.clear_playlist()

        self.media_files.extend(files) # Add the selected songs to the playlist

        self.playlist_list.addItems([os.path.basename(file) for file in files]) # Display the Songnames in the playlist

    def play_selected(self) -> None:
        """Play the selected item in the playlist."""        
        # Play the selected item in the playlist
        current_item = self.playlist_list.currentItem()
        if current_item:
            self.current_index = self.playlist_list.row(current_item)
            self.play_next()

    def play_next(self, media_file: str | None = None) -> None:
        """Play the next song in the playlist."""        
        # Check if there are any files in the playlist
        if not self.media_files:
            return

        self.play_button.setText(self.tr("Pause"))
        self.progress_slider.setDisabled(False)
        if not media_file:
            self.current_music = self.media_files[self.current_index]
        else: self.current_music = media_file

        self.update_current_song()
        pygame.mixer.music.load(self.current_music)
        pygame.mixer.music.play()

        # Get the length of the music in seconds and set the slider's range
        self.music_length = pygame.mixer.Sound(self.current_music).get_length()
        self.progress_slider.setRange(0, int(self.music_length))

    def update_progress(self) -> None:
        """Update the progress slider."""        
        if not pygame.mixer.music.get_busy():
            self.progress_slider.setDisabled(True)
            return
        # Get current position of the audio file and update the slider
        current_position = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
        self.progress_slider.blockSignals(True)  # Prevent triggering seek_audio while updating
        self.progress_slider.setValue(int(self.start_value + current_position))
        self.progress_slider.blockSignals(False)

    def seek_audio(self) -> None:
        """set the audio to the selected position"""        
        # When the user clicks on the slider, move the audio to the selected position
        self.start_value: float = self.progress_slider.value()
        pygame.mixer.music.set_pos(self.start_value)

    def closeEvent(self, event):
        if self.playlist_thread:
            self.playlist_thread.stop()
        self.settings_handler.save()

        pygame.mixer.quit()
        event.accept()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app: QApplication = QApplication(sys.argv)
    player: Mp3Player = Mp3Player(os.path.join(os.environ["USERPROFILE"], "Music"))
    player.show()
    sys.exit(app.exec())
