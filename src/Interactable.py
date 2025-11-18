import pygame
from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR
from utils import resource_path

class _Interactable(_Obstacle):
    """
    Clase única para todos los objetos interactuables.
    Hereda de _Obstacle (que también es data-driven).
    Toda la lógica (parpadeo, ocultar, tipo de interacción) 
    está contenida aquí y se configura a través del 
    diccionario 'data' en el __init__.
    """
    def __init__(self, data: dict):
        """
        Inicializa el objeto interactuable desde un diccionario de datos (del JSON).
        """
        super().__init__(data) 
        
        self.interaction_type = data.get("interaction_type", "None")
        self.interaction_data = data.get("interaction_data", None)
        
        self.interacted_once = False
        self.is_hidden = data.get("starts_hidden", False)
        
        self.is_interacting = False
        self.interaction_duration = 30
        self.interaction_timer = 0
        self.original_image = self.image.copy()
        
        flash_path = data.get("flash_image_path")
        try:
            if not flash_path:
                raise pygame.error("No flash image path provided")
                
            self.flash_image = pygame.image.load(resource_path(flash_path)).convert_alpha()
            self.flash_image = pygame.transform.scale(
                self.flash_image, (self.image.get_width(), self.image.get_height())
            )
        except pygame.error as e:
            print(f"ADVERTENCIA: No se pudo cargar '{flash_path}' ({e}). Usando destello blanco.")
            self.flash_image = self.original_image.copy()
            self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_ADD)

    def unhide(self):
        """
        Hace que el objeto sea visible y, por lo tanto, interactuable.
        (Migrado de la clase Image).
        """
        self.is_hidden = False

    def interact(self):
        """
        Inicia la interacción.
        (Migrado de _NoteHolder e Image).
        """
        if self.is_hidden:
            return None
        
        if self.interacted_once or self.is_interacting:
            return None
        
        self.is_interacting = True
        self.interaction_timer = self.interaction_duration
        return "interaction_started"
    
    def read(self):
        """
        Finaliza la interacción, se auto-destruye (del grupo de sprites)
        y devuelve los datos de la interacción.
        """
        self.interacted_once = True
        self.kill()
        
        return self.interaction_data
    
    def update(self):
        """
        Actualiza el estado del objeto cada frame.
        """
        super().update() 
        
        if not self.is_interacting:
            return None

        self.interaction_timer -= 1
        if self.interaction_timer > 0:
            if (self.interaction_timer // 10) % 2 == 0: 
                self.image = self.flash_image
            else:
                self.image = self.original_image
        else:
            self.is_interacting = False
            self.image = self.original_image
            return "interaction_finished"
        
        return None