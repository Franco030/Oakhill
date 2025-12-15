import pygame
from abc import ABC, abstractmethod

class GameResult(ABC):
    """
    Abstract class to handle actions results
    """

    @abstractmethod
    def execute(self, game):
        """
        Executes the logic of the result
        :param game_context: Game instance (self in Game.py)
        """
        pass

class NoteResult(GameResult):
    def __init__(self, note_data, blocking=False):
        self.note_data = note_data
        self.blocking = blocking

    def execute(self, game):
        game.ui_manager.show_note(self.note_data, blocking=self.blocking)

class DialogueResult(GameResult):
    def __init__(self, data, blocking=False, pause_music=False):
        self.dialogue_data = data
        self.blocking = blocking
        self.pause_music = pause_music

    def execute(self, game):
        game.ui_manager.show_dialogue(
            self.dialogue_data, 
            blocking=self.blocking, 
            resume_music_on_close=self.pause_music
        )

class ChoiceResult(GameResult):
    def __init__(self, text, flag_name, blocking=True):
        self.text = text
        self.flag_name = flag_name
        self.blocking = blocking

    def execute(self, game):
        game.ui_manager.show_choice(self.text, self.flag_name, blocking=self.blocking)

class ImageResult(GameResult):
    def __init__(self, image_path, blocking=False, pause_music=False):
        self.image_path = image_path
        self.blocking = blocking
        self.pause_music = pause_music

    def execute(self, game):
        game.ui_manager.show_image(self.image_path, blocking=self.blocking)
        if self.pause_music:
            pygame.mixer.music.pause()

class AnimationResult(GameResult):
    def __init__(self, image_list, speed=0.1, blocking=False, loop=True, pause_music=False):
        self.image_list = image_list
        self.speed = speed
        self.blocking = blocking
        self.loop = loop
        self.pause_music = pause_music

    def execute(self, game):
        game.ui_manager.show_animation(
            self.image_list, 
            speed=self.speed, 
            blocking=self.blocking, 
            loop=self.loop
        )
        if self.pause_music:
            pygame.mixer.music.pause()

class DestroyResult(GameResult):
    def __init__(self, target_id):
        self.target_id = target_id

    def execute(self, game):
        if game.level_manager.current_scene:
            game.level_manager.current_scene.remove_object_by_id(self.target_id)

class WaitResult(GameResult):
    def __init__(self, duration):
        """
        :param duration: Wait time in seconds only for the script or user input
        """
        self.duration = duration
        self.blocking = True

    def execute(self, game):
        pass