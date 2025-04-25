import json
import gzip
import os


class SavedPlaylistsHandler:
    """Class to handle the saved Playlists."""
    def __init__(self) -> None:
        """Initialize the saved Playlists handler."""
        self.playlists_path: str = str(os.path.join(os.getenv("LOCALAPPDATA"),
                                                "Mp3_Player",
                                                "Playlists"
                                                ))

        self.playlist_tester: PlaylistTester = PlaylistTester()

    def get_playlist(self, name: str) -> list[str]:
        """Get the playlist for its name
        
        Args:
        """
        if not os.path.isdir(self.playlists_path):
            return []

        file_path: str = os.path.join(self.playlists_path, name)
        playlist: list[str] = []

        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            playlist = json.load(file)


        return self.playlist_tester.test_playlist(name, playlist)

    def load_names(self) -> list[str]:
        """Load the saved Playlist's names.

        Returns:
            list[str]: The saved Playlist's name.
        """
        if not os.path.isdir(self.playlists_path):
            return []

        names: list[str] = os.listdir(self.playlists_path)

        return names

    def load_playlists(self) -> dict[str, list[str]]: # unused
        """Load the saved Playlists.

        Returns:
            dict[str, list[str]]: The saved Playlists (dict[playlist_name, playlist]).
        """
        if not os.path.isdir(self.playlists_path):
            return {}

        names: list[str] = os.listdir(self.playlists_path)
        file_paths: list[str] = [os.path.join(self.playlists_path, name) for name in names]
        playlists: dict[str, list[str]] = {}

        for file_path, name in zip(file_paths, names):
            with gzip.open(file_path, "rt", encoding="utf-8") as file:
                playlists[os.path.splitext(name)[0]] = json.load(file)

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
        with gzip.open(file_path, "wt", encoding="utf-8") as file:
            json.dump(playlist, file)  # Save the playlist in JSON format with compression

    def remove_from_playlist(self, playlist_name: str, song_path: str) -> None:
        """Remove a song from a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
            song_path (str): The path of the song to remove.
        """
        playlist: list[str] = self.get_playlist(playlist_name + ".json")
        if not playlist: return

        playlist.remove(song_path)
        self.save_playlist(playlist_name, playlist)

    def add_to_playlist(self, playlist_name: str, song_path: str) -> None:
        """Add a song to a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
            song_path (str): The path of the song to add.
        """
        if not playlist_name + ".json" in self.load_names():
            self.save_playlist(playlist_name, [song_path])
            return
        playlist: list[str] = self.get_playlist(playlist_name + ".json")
        playlist.append(song_path)
        self.save_playlist(playlist_name, playlist)

    def delete_playlist(self, playlist_name: str) -> None:
        """Delete a Playlist.

        Args:
            playlist_name (str): The name of the Playlist.
        """
        if not playlist_name + ".json" in self.load_names():
            return
        os.remove(os.path.join(self.playlists_path, f"{playlist_name}.json"))


class PlaylistTester:
    def test_all(self, playlists: dict[str, list[str]]) -> dict[str, list[str]]:
        for name, playlist in playlists.items():
            playlist = self.test_playlist(name, playlist)
            playlists[name] = playlist

        return playlists

    def test_playlist(self, name: str, playlist: list[str]) -> list[str]:
        if not (name or playlist):
            return []

        playlist: list[str] = [path for path in playlist if os.path.isfile(path)]

        return playlist


if __name__ == "__main__":
    loader: SavedPlaylistsHandler = SavedPlaylistsHandler()
    names: list[str] = loader.load_names()
    for name in names:
        playlist: list[str] = loader.get_playlist(name)
        print(f"Playlist: {name} -- lenght: {len(playlist)}")
