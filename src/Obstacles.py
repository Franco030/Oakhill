import pygame
from .Game_Constants import RESIZE_FACTOR
from .Animations import Animation
from utils import resource_path

class _Obstacle(pygame.sprite.Sprite):
    """
    Clase única para todos los obstáculos estáticos (no interactuables).
    Toda la configuración (imagen, hitbox, animación) se carga 
    desde el diccionario 'data' en el __init__.
    """
    def __init__(self, data: dict):
        """
        Inicializa el obstáculo desde un diccionario de datos (del JSON).
        """
        super().__init__()

        
        image_path = data.get("image_path")
        resize_factor = data.get("resize_factor", RESIZE_FACTOR)

        try:
            if not image_path or image_path == "None":
                raise ValueError("Ruta de imagen es 'None' o está vacía.")
                
            self.image = pygame.image.load(resource_path(image_path)).convert_alpha()
            
            self.image = pygame.transform.scale(self.image, 
                (int(self.image.get_width() * resize_factor), int(self.image.get_height() * resize_factor))
            )
            
        except Exception as e:
            print(f"INFO: No se pudo cargar la imagen '{image_path}': {e}. Creando placeholder.")
            self.image = pygame.Surface((int(20 * resize_factor), int(20 * resize_factor)))
            self.image.fill((255, 0, 255))
            self.image.set_alpha(150) 
        

        self.is_ground = data.get("is_ground", False)
        
        self.rect = self.image.get_rect(center=(data["x"], data["y"]))


        if data.get("is_passable", False):

            self._collision_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 0, 0)
        else:
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            self._collision_rect = pygame.Rect(
                self.rect.left + offset[0],
                self.rect.top + offset[1],
                self.rect.width + offset[2],
                self.rect.height + offset[3]
            )
        
        self.animation = None
        animation_paths = data.get("animation_images")
        if animation_paths:
            try:
                images = [resource_path(p) for p in animation_paths]
                if images:
                    self.animation = Animation(self, images, data.get("animation_speed", 0.1))
            except Exception as e:
                print(f"ERROR: No se pudo cargar la animación para {data.get('id')}: {e}")

    def update(self):
        """
        Este método es llamado por el grupo de sprites en main_window.
        Es crucial para las animaciones.
        """
        if self.animation:
            self.animation.animate()

    @property
    def collision_rect(self):
        """
        Devuelve el hitbox personalizado.
        """
        return self._collision_rect

    def collides_with(self, other_sprite):
        """
        Comprueba la colisión usando el hitbox personalizado.
        """
        return self._collision_rect.colliderect(other_sprite.collision_rect)