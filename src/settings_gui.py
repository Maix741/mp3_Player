from pathlib import Path
import os, sys

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QSlider, QVBoxLayout, QFileDialog, QLabel, QWidget, QLineEdit,
    QSpacerItem, QSizePolicy, QMainWindow, QHBoxLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt


class SettingsGUI(QMainWindow):
    def __init__(self, settings_handler, translator, parent=None) -> None:
        super(SettingsGUI, self).__init__(parent)

        self.settings_handler = settings_handler
        self.restart_required: bool = False


        self.translator = translator
        QCoreApplication.installTranslator(self.translator)

        # Create a central widget and set it as the main window's central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a layout for the central widget
        self.layout = QVBoxLayout(self.central_widget)

        self.setWindowTitle(self.tr("Settings"))
        self.setGeometry(100, 100, 400, 250)

        self.init_ui()

    def init_ui(self) -> None:
        # Initial Directory Setting
        initial_directory_label = QLabel(self.tr("Initial Directory:"))
        self.initial_directory_display = QLineEdit(self.settings_handler.get("initial_directory"))
        self.initial_directory_display.setReadOnly(True)
        initial_directory_button = QPushButton(self.tr("Select Initial Directory"))
        initial_directory_button.clicked.connect(self.select_initial_directory)

        initial_directory_layout: QHBoxLayout = QHBoxLayout()
        initial_directory_layout.addWidget(initial_directory_label)
        initial_directory_layout.addWidget(self.initial_directory_display)
        initial_directory_layout.addWidget(initial_directory_button)

        # Language Selection
        system_locale_label = QLabel(self.tr("Language:"))
        self.system_locale_option = QComboBox()
        self.system_locale_option.addItems(self.get_possible_locales())
        self.system_locale_option.setCurrentText(self.settings_handler.get("system_locale"))
        self.system_locale_option.currentTextChanged.connect(self.set_locale)

        language_layout: QHBoxLayout = QHBoxLayout()
        language_layout.addWidget(system_locale_label)
        language_layout.addWidget(self.system_locale_option)

        # Volume
        volume_label = QLabel(self.tr("Default volume:"))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.settings_handler.get("volume")))
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.volume_input = QLineEdit()
        self.volume_input.setFixedWidth(30)
        self.volume_input.setText(str(self.settings_handler.get("volume")))
        self.volume_input.textChanged.connect(self.set_volume)

        volume_layout: QHBoxLayout = QHBoxLayout()
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_input)

        # Shuffle
        shuffle_label = QLabel(self.tr("Shuffle:"))
        self.shuffle_option = QComboBox()
        self.shuffle_option.addItems([self.tr("True"), self.tr("False")])
        self.shuffle_option.setCurrentText(self.tr("True") if self.settings_handler.get("shuffle") else self.tr("False"))
        self.shuffle_option.currentTextChanged.connect(self.set_shuffle)

        shuffle_layout: QHBoxLayout = QHBoxLayout()
        shuffle_layout.addWidget(shuffle_label)
        shuffle_layout.addWidget(self.shuffle_option)

        # Load Saved Playlists
        load_saved_playlist_label = QLabel(self.tr("Load Saved Playlist:"))
        self.load_saved_playlist_option = QComboBox()
        self.load_saved_playlist_option.addItems([self.tr("True"), self.tr("False")])
        self.load_saved_playlist_option.setCurrentText(self.tr("True") if self.settings_handler.get("load_saved_playlist") else self.tr("False"))
        self.load_saved_playlist_option.currentTextChanged.connect(self.set_load_saved_playlist)

        load_saved_layout: QHBoxLayout = QHBoxLayout()
        load_saved_layout.addWidget(load_saved_playlist_label)
        load_saved_layout.addWidget(self.load_saved_playlist_option)

        # design
        design_label = QLabel(self.tr("Window Design:"))
        self.design_option = QComboBox()
        self.design_option.addItems([self.tr("System design"), self.tr("Dark"), self.tr("Light")])
        self.design_option.setCurrentText(self.settings_handler.get("design") or self.tr("System design"))
        self.design_option.currentTextChanged.connect(self.set_design)

        design_layout: QHBoxLayout = QHBoxLayout()
        design_layout.addWidget(design_label)
        design_layout.addWidget(self.design_option)

        # Add layouts to main layout
        self.layout.addLayout(initial_directory_layout)
        self.layout.addLayout(language_layout)
        self.layout.addLayout(volume_layout)
        self.layout.addLayout(shuffle_layout)
        self.layout.addLayout(load_saved_layout)
        self.layout.addLayout(design_layout)

        # Spacer
        self.layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Save and Save and Restart buttons layout
        buttons_layout = QHBoxLayout()

        # Save button
        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.clicked.connect(self.save_settings_and_close)
        buttons_layout.addWidget(self.save_button)

        # Save and restart button
        self.save_restart_button = QPushButton(self.tr("Save and Restart"))
        self.save_restart_button.clicked.connect(self.save_settings_and_restart)
        # self.buttons_layout.addWidget(self.save_restart_button)

        self.layout.addLayout(buttons_layout)

    """
    def init_ui_old(self) -> None:
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.form_layout = QHBoxLayout()

        self.labels_layout = QVBoxLayout()
        self.settings_layout = QVBoxLayout()

        # Initial Directory
        self.initial_directory_label = QLabel(self.tr("Initial Directory:"))
        self.labels_layout.addWidget(self.initial_directory_label)

        self.initial_directory_display = QLabel(self.settings_handler.get("initial_directory"))
        self.settings_layout.addWidget(self.initial_directory_display)

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

        self.volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.settings_handler.get("volume")))
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_layout.addWidget(self.volume_slider)

        self.volume_input = QLineEdit()
        self.volume_input.setFixedWidth(30)
        self.volume_input.setText(str(self.settings_handler.get("volume")))
        self.volume_input.textChanged.connect(self.set_volume)
        self.volume_layout.addWidget(self.volume_input)

        self.settings_layout.addLayout(self.volume_layout)

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

        # design
        self.design_label = QLabel(self.tr("Window Design:"))
        # self.labels_layout.addWidget(self.design_label)

        self.design_option = QComboBox()
        self.design_option.addItems([self.tr("System design"), self.tr("Dark"), self.tr("Light")])
        self.design_option.setCurrentText(self.settings_handler.get("design") or self.tr("System design"))
        self.design_option.currentTextChanged.connect(self.set_design)
        # self.settings_layout.addWidget(self.design_option)


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
        self.save_button.clicked.connect(self.save_settings_and_close)
        self.buttons_layout.addWidget(self.save_button)

        # Save and restart button
        # self.save_restart_button = QPushButton(self.tr("Save and Restart"))
        # self.save_restart_button.clicked.connect(self.save_settings_and_restart)
        # self.buttons_layout.addWidget(self.save_restart_button)

        self.main_layout.addLayout(self.buttons_layout)

        self.setWidget(self.main_widget)
    """

    def save_settings_and_close(self) -> None:
        """Save the current settings and close the settings window.
        """
        if self.restart_required:
            QMessageBox.information(self, self.tr("Restart required"), self.tr("Restarting the app is required\n for all changes to take affect"))
        self.settings_handler.save()
        self.close()

    def save_settings_and_restart(self) -> None:
        self.settings_handler.save()
        QCoreApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def select_initial_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select Initial Directory"))
        if directory:
            self.settings_handler.set("initial_directory", directory)
            self.initial_directory_display.setText(directory)

    def set_volume(self, value: int) -> None:
        if not value and not str(value).isdigit():
            value: int = 0
        elif int(value) > 100:
            value: int = 100
        self.volume_input.setText(str(value))
        self.volume_slider.setValue(int(value))
        self.settings_handler.set("volume", int(value))

    def set_locale(self) -> None:
        self.restart_required: bool = True
        self.settings_handler.set("system_locale", self.system_locale_option.currentText())

    def set_shuffle(self) -> None:
        self.settings_handler.set("shuffle", self.shuffle_option.currentText() == self.tr("True"))

    def set_load_saved_playlist(self) -> None:
        self.settings_handler.set("load_saved_playlist", self.load_saved_playlist_option.currentText() == self.tr("True"))

    def set_design(self) -> None:
        self.settings_handler.set("design", self.design_option.currentText() == self.tr("True"))
        self.restart_required: bool = True

    def closeEvent(self, event) -> None:
        self.settings_handler.save()
        event.accept()

    def get_possible_locales(self) -> list[str]:
        if not hasattr(self, "_cached_locales"):
            current_dir = os.path.dirname(sys.argv[0])
            if current_dir.endswith(("src", "bin")):
                locales_path = os.path.join(Path(current_dir).parent, "locales")
            else: # Running from root directory
                locales_path = os.path.join(current_dir, "locales")

            self._cached_locales = [locale.rstrip(".qm") for locale in os.listdir(locales_path) if locale.endswith(".qm")]
        return self._cached_locales


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
