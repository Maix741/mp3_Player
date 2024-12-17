from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider, QVBoxLayout, QHBoxLayout, QListWidget, QFileDialog, QLabel, QMenuBar, QMenu, QWidget, QSpacerItem, QSizePolicy, QDockWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction


class Menu_Bar(QMainWindow):
    def __init__(self, parent = ..., flags = ...):
        super().__init__(parent, flags)
        
        # Create "File" menu
        # file_menu = QMenu("File", self)
        # menubar.addMenu(file_menu)

        # # Add actions to the "File" menu
        # open_action = QAction("Open", self)
        # open_action.triggered.connect(self.load_single_files)
        # file_menu.addAction(open_action)

        # exit_action = QAction("Exit", self)
        # exit_action.triggered.connect(self.close)
        # file_menu.addAction(exit_action)
