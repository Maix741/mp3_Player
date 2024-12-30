import os
import json


class Saved_Playlists_handler:
    def __init__(self):
        self.playlists_path: str = str(os.path.join(os.getenv("LOCALAPPDATA"),
                                                "Mp3_Player",
                                                "Playlists"
                                                ))

    def load_playlists(self) -> dict[str, list[str]]:
        if not os.path.isdir(self.playlists_path):
            return {}

        names: list[str] = os.listdir(self.playlists_path)
        file_paths: list[str] = [os.path.join(self.playlists_path, name) for name in names]
        playlists: dict[str, str] = {}

        for file_path, name in zip(file_paths, names):
            with open(file_path, "r") as file:
                playlists[name.split(".")[0]] = json.load(file)

        return playlists

    def save_playlist(self, playlist_name: str, playlist: list[str]):
        if not os.path.isdir(self.playlists_path):
            os.makedirs(self.playlists_path)

        file_path = os.path.join(self.playlists_path, f"{playlist_name}.json")
        with open(file_path, "w") as file:
            json.dump(playlist, file)  # Save the playlist in JSON format

    def remove_from_playlist(self, playlist_name: str, song_path: str):
        if not playlist_name in self.load_playlists().keys():
            return
        playlist = self.load_playlists().get(playlist_name, [])
        playlist.remove(song_path)
        self.save_playlist(playlist_name, playlist)

    def add_to_playlist(self, playlist_name: str, song_path: str):
        if not playlist_name in self.load_playlists().keys():
            self.save_playlist(playlist_name, [song_path])
            return
        playlist = self.load_playlists().get(playlist_name, [])
        playlist.append(song_path)
        self.save_playlist(playlist_name, playlist)

if __name__ == "__main__":
    loader = Saved_Playlists_handler()
    print(loader.load_playlists())