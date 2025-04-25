import pygame


class MusicHandler:
    def __init__(self) -> None:
        pygame.init()

    def change_music_pos(self, set_to) -> None:
        pygame.mixer.music.set_pos(set_to)

    def set_volume(self, set_to: float | int) -> None:
        pygame.mixer.music.set_volume(set_to)

    def get_lenght(self, path_to_file: str) -> float:
        return pygame.mixer.Sound(path_to_file).get_length()

    def get_current_pos(self) -> int:
        return pygame.mixer.music.get_pos()

    def load_and_play(self, path_to_file: str) -> None:
        pygame.mixer.music.load(path_to_file)
        pygame.mixer.music.play()

    def stop_and_unload(self) -> None:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def pause(self) -> None:
        pygame.mixer.music.pause()

    def unpause(self) -> None:
        pygame.mixer.music.unpause()

    def unloop(self) -> None:
        if pygame.mixer.music.get_endevent() == pygame.constants.USEREVENT:
            pygame.mixer.music.set_endevent()
            return True

        return False

    def loop(self) -> None:
        if pygame.mixer.music.get_endevent() != pygame.constants.USEREVENT:
            pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
            return True

        return False

    def terminate(self) -> None:
        self.stop_and_unload()
        # pygame.mixer.quit()
