import pygame
import os
from utils import resource_path

class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance.images = {}
            cls._instance.sounds = {}
            cls._instance.fonts = {}
            cls._instance._placeholder = None
        return cls._instance
    
    def get_image(self, relative_path):
        if not relative_path or relative_path == "None":
            return None

        if relative_path in self.images:
            return self.images[relative_path]

        full_path = resource_path(relative_path)

        try:
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Error: File not found '{full_path}'")
                return self._get_placeholder()

            surface = pygame.image.load(full_path).convert_alpha()

            self.images[relative_path] = surface
            print(f"[ResourceManager] Loaded and cached: {relative_path}") # Descomentar para debug
            return surface

        except Exception as e:
            print(f"[ResourceManager] Critical Error loading '{relative_path}': {e}")
            return self._get_placeholder()

    def get_font(self, size):
        if size not in self.fonts:
            try:
                font_path = resource_path("assets/fonts/little-pixel.ttf")
                font = pygame.font.Font(font_path, size)
                self.fonts[size] = font
                print(f"[ResourceManager] Loaded Global Font size {size}")
            except Exception as e:
                print(f"[ResourceManager] Error loading font size {size}: {e}")
                self.fonts[size] = pygame.font.SysFont("Arial", size)
            
        return self.fonts[size]

    def play_music(self, relative_path, volume=0.6, loops=-1, fade_ms=500):
        try:
            full_path = resource_path(relative_path)
            
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Error: Music file not found at {full_path}")
                return


            if self.current_music == relative_path: return

            print(f"[ResourceManager] Playing music: {relative_path}")
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            
        except Exception as e:
            print(f"[ResourceManager] Critical Error loading music '{relative_path}': {e}")

    def load_images_from_list(self, file_paths):
        loaded_images = []
        for path in file_paths:
            img = self.get_image(path)
            if img:
                loaded_images.append(img)
        return loaded_images
    
    def _get_placeholder(self):
        if self._placeholder is None:
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))
            self._placeholder = surface
        return self._placeholder

    def clear_cache(self):
        count = len(self.images)
        self.images.clear()
        # self.sounds.clear()
        print(f"[ResourceManager] Cache cleared. Released {count} textures.")
    
    def load_all_sounds(self, folder_relative_path):
        full_path = resource_path(folder_relative_path)
        valid_ext = ('.wav', '.mp3', '.ogg')

        if not os.path.exists(full_path):
            return {}

        print(f"[ResourceManager] Bulk loading sounds from: {folder_relative_path}...")
        for root, _, files in os.walk(full_path):
            for filename in files:
                if filename.lower().endswith(valid_ext):
                    key_name = os.path.splitext(filename)[0]
                    file_path = os.path.join(root, filename)
                    try:
                        self.sounds[key_name] = pygame.mixer.Sound(file_path)
                    except Exception as e:
                        print(f"  -> Error: {e}")
        return self.sounds
    
    # --- Deprecated Functions (but I keep them for compatibility) --- 

    def load_all_images(self, folder_relative_path):
        full_path = resource_path(folder_relative_path)
        valid_ext = ('.png', '.jpg', '.jpeg')

        if not os.path.exists(full_path): return {}

        for root, _, files in os.walk(full_path):
            for filename in files:
                if filename.lower().endswith(valid_ext):
                    file_path = os.path.join(root, filename)
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        key_name = os.path.splitext(filename)[0]
                        self.images[key_name] = img 
                    except Exception: pass
        return self.images

# Global Instance
resource_manager = ResourceManager()