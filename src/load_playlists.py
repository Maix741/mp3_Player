import json
import os


class Saved_Playlists_handler:
    """Class to handle the saved Playlists."""
    def __init__(self) -> None:
        """Initialize the saved Playlists handler."""
        self.playlists_path: str = str(os.path.join(os.getenv("LOCALAPPDATA"),
                                                "Mp3_Player",
                                                "Playlists"
                                                ))


    def load_playlists(self) -> dict[str, list[str]]:
        """Load the saved Playlists.
        
        Returns:
            dict[str, list[str]]: The saved Playlists (dict[playlist_name, playlist]).
        """
        if not os.path.isdir(self.playlists_path):
            return {}

        names: list[str] = os.listdir(self.playlists_path)
        file_paths: list[str] = [os.path.join(self.playlists_path, name) for name in names]
        playlists: dict[str, str] = {}

        for file_path, name in zip(file_paths, names):
            with open(file_path, "r") as file:
                playlists[name.split(".")[0]] = json.load(file)

        return playlists

    def save_playlist(self, playlist_name: str, playlist: list[str]) -> None:
        """Save a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
            playlist (list[str]): The Playlist to save.
        """
        if not os.path.isdir(self.playlists_path):
            os.makedirs(self.playlists_path)

        file_path = os.path.join(self.playlists_path, f"{playlist_name}.json")
        with open(file_path, "w") as file:
            json.dump(playlist, file)  # Save the playlist in JSON format

    def remove_from_playlist(self, playlist_name: str, song_path: str) -> None:
        """Remove a song from a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
            song_path (str): The path of the song to remove.
        """
        if not playlist_name in self.load_playlists().keys():
            return
        playlist = self.load_playlists().get(playlist_name, [])
        playlist.remove(song_path)
        self.save_playlist(playlist_name, playlist)

    def add_to_playlist(self, playlist_name: str, song_path: str) -> None:
        """Add a song to a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
            song_path (str): The path of the song to add.
        """
        if not playlist_name in self.load_playlists().keys():
            self.save_playlist(playlist_name, [song_path])
            return
        playlist = self.load_playlists().get(playlist_name, [])
        playlist.append(song_path)
        self.save_playlist(playlist_name, playlist)

    def delete_playlist(self, playlist_name: str) -> None:
        """Delete a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
        """
        if not playlist_name in self.load_playlists().keys():
            return
        os.remove(os.path.join(self.playlists_path, f"{playlist_name}.json"))


if __name__ == "__main__":
    loader = Saved_Playlists_handler()
    print(loader.load_playlists())