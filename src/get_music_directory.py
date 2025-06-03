import platform
import os


def get_music_directory() -> str:
    if platform.system() == "Windows":    # Windows
        music_directory: str = os.path.join(os.environ.get("USERPROFILE", ""), "Music")

    elif platform.system() == "Darwin":    # macOS
        music_directory: str = os.path.join(os.environ.get("HOME", ""), "Music")

    else:    # Linux and other Unix-like systems
        music_directory: str = os.path.expanduser("~/Music")

    return music_directory
