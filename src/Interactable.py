from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR

class _Interactable(_Obstacle):
    """
    Base class for interactable objects in the game.
    Inherits from _Obstacle to be visible.
    """
    def __init__(self, start_x, start_y, image, resize_factor=None):
        super().__init__(start_x, start_y, image, resize_factor)
        self.interacted_once = False

    def interact():
        """
        Method to be overridden by subclasses to define interaction behavior.
        """
        pass


class Note(_Interactable):
    """
    An interactable object representing a note that the player can read.
    """
    image_path = 'assets/images/note.png' 
    images = [image_path] # Requirement for Asset_Config

    def __init__(self, start_x, start_y, index_image=0):
        super().__init__(start_x, start_y, self.image_path, RESIZE_FACTOR)

        self.note_text_content = [
            "Línea 1: El fantasma blanco es... tímido.",
            "Línea 2: Parece que se asusta cuando le 'hablas'.",
            "",
            "Línea 4: ...pero siempre vuelve."
        ]

    def interact(self):
        """
        Displays the note's text content when the player interacts with it.
        """
        self.interacted_once = True
        return self.note_text_content
