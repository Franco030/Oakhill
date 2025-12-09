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
            cls._instance.current_music = None
            cls._instance.asset_map = {}
            cls._instance.load_manifest()
        return cls._instance
    
    def load_manifest(self):
        import json
        
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_dir)
            path = os.path.join(project_root, "data", "assets.json")
            
            if not os.path.exists(path):
                print(f"[ResourceManager] WARNING: Manifest not found at {path}")
                return

            with open(path, "r") as f:
                data = json.load(f)
                self.asset_map.update(data.get("textures", {}))
                self.asset_map.update(data.get("sounds", {}))
                
            print(f"[ResourceManager] Manifest loaded. {len(self.asset_map)} assets registered.")
            
        except Exception as e:
            print(f"[ResourceManager] Error loading manifest: {e}")
    
    def get_image(self, key_or_path):
        if not key_or_path or key_or_path == "None": return None

        real_path = self.asset_map.get(key_or_path, key_or_path)

        if real_path in self.images:
            return self.images[real_path]

        try:
            full_path = resource_path(real_path)
            
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Error: File not found '{full_path}' (Key: {key_or_path})")
                return self._get_placeholder()

            surface = pygame.image.load(full_path).convert_alpha()
            
            self.images[real_path] = surface
            return surface

        except Exception as e:
            print(f"[ResourceManager] Critical Error loading '{real_path}': {e}")
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
            real_path = self.asset_map.get(relative_path, relative_path)
            
            if self.current_music == real_path: return

            full_path = resource_path(real_path)
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Music not found: {full_path}")
                return

            print(f"[ResourceManager] Playing music: {real_path}")
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            
            self.current_music = real_path
            
        except Exception as e:
            print(f"[ResourceManager] Error music '{relative_path}': {e}")

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