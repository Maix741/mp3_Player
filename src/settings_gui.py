from pathlib import Path
import os, sys

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QSlider, QVBoxLayout, QFileDialog, QLabel, QMenu, QWidget, 
    QSpacerItem, QSizePolicy, QDockWidget, QScrollArea, QInputDialog, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtCore import QCoreApplication


class SettingsGUI(QDockWidget):
    def __init__(self, settings_handler, translator, parent=None) -> None:
        super().__init__(parent)

        self.settings_handler = settings_handler

        self.setWindowTitle(self.tr("Settings"))
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

        self.translator = translator
        QCoreApplication.installTranslator(self.translator)

        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.form_layout = QHBoxLayout()

        self.labels_layout = QVBoxLayout()
        self.settings_layout = QVBoxLayout()

        # Initial Directory
        self.initial_directory_label = QLabel(self.tr("Initial Directory:"))
        self.labels_layout.addWidget(self.initial_directory_label)

        self.initial_directory_button = QPushButton(self.tr("Select Initial Directory"))
        self.initial_directory_button.clicked.connect(self.select_initial_directory)
        self.settings_layout.addWidget(self.initial_directory_button)

        # System Locale
        self.system_locale_label = QLabel(self.tr("Language:"))
        self.labels_layout.addWidget(self.system_locale_label)

        self.system_locale_option = QComboBox()
        self.system_locale_option.addItems(self.get_possible_locales())
        self.system_locale_option.setCurrentText(self.settings_handler.get("system_locale"))
        self.system_locale_option.currentTextChanged.connect(self.set_locale)

        self.settings_layout.addWidget(self.system_locale_option)

        # Volume
        self.volume_label = QLabel(self.tr("Default volume:"))
        self.labels_layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.settings_handler.get("volume"))
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.settings_layout.addWidget(self.volume_slider)

        # Shuffle
        self.shuffle_label = QLabel(self.tr("Shuffle:"))
        self.labels_layout.addWidget(self.shuffle_label)

        self.shuffle_option = QComboBox()
        self.shuffle_option.addItems([self.tr("True"), self.tr("False")])
        self.shuffle_option.setCurrentText(self.tr("True") if self.settings_handler.get("shuffle") else self.tr("False"))
        self.shuffle_option.currentTextChanged.connect(self.set_shuffle)
        self.settings_layout.addWidget(self.shuffle_option)

        # Load Saved Playlists
        self.load_saved_playlist_label = QLabel(self.tr("Load Saved Playlist:"))
        self.labels_layout.addWidget(self.load_saved_playlist_label)

        self.load_saved_playlist_option = QComboBox()
        self.load_saved_playlist_option.addItems([self.tr("True"), self.tr("False")])
        self.load_saved_playlist_option.setCurrentText(self.tr("True") if self.settings_handler.get("load_saved_playlist") else self.tr("False"))
        self.load_saved_playlist_option.currentTextChanged.connect(self.set_load_saved_playlist)
        self.settings_layout.addWidget(self.load_saved_playlist_option)

        # Add layouts to main layout
        self.form_layout.addLayout(self.labels_layout)
        self.form_layout.addLayout(self.settings_layout)
        self.main_layout.addLayout(self.form_layout)

        # Spacer
        self.main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Save and Save and Restart buttons layout
        self.buttons_layout = QHBoxLayout()

        # Save button
        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.save_button)

        # Save and restart button
        self.save_restart_button = QPushButton(self.tr("Save and Restart"))
        self.save_restart_button.clicked.connect(lambda: [self.settings_handler.save(), os.execl(sys.executable, sys.executable, *sys.argv)])
        self.buttons_layout.addWidget(self.save_restart_button)

        self.main_layout.addLayout(self.buttons_layout)

        self.setWidget(self.main_widget)

    def select_initial_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select Initial Directory"))
        if directory:
            self.settings_handler.set("initial_directory", directory)

    def set_volume(self, value: int) -> None:
        self.settings_handler.set("volume", value)

    def set_locale(self) -> None:
        self.settings_handler.set("system_locale", self.system_locale_option.currentText())

    def set_shuffle(self) -> None:
        self.settings_handler.set("shuffle", self.shuffle_option.currentText() == self.tr("True"))

    def set_load_saved_playlist(self) -> None:
        self.settings_handler.set("load_saved_playlist", self.load_saved_playlist_option.currentText() == self.tr("True"))

    def closeEvent(self, event) -> None:
        self.settings_handler.save()
        event.accept()

    def get_possible_locales(self) -> list[str]:
        current_dir = os.path.dirname(sys.argv[0])
        if current_dir.endswith(("src", "bin")):
            locales_path = os.path.join(Path(current_dir).parent, "locales")
        else: # Running from root directory
            locales_path = os.path.join(current_dir, "locales")

        return [locale.rstrip(".qm") for locale in os.listdir(locales_path) if locale.endswith(".qm")]


if __name__ == "__main__":
    from settings_handler import SettingsHandler
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTranslator

    translator: QTranslator = QTranslator()
    app: QApplication = QApplication(sys.argv)
    handler = SettingsHandler()
    window = SettingsGUI(handler, translator)
    window.show()
    sys.exit(app.exec())