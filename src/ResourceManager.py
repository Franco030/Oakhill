import pygame
import os
import json
from utils import resource_path

class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance.images = {}
            cls._instance.sounds = {}
            cls._instance.fonts = {}
            cls._instance.asset_map = {}
            cls._instance._placeholder = None
            cls._instance.current_music = None
            
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            cls._instance.load_manifest()
        return cls._instance
    
    def load_manifest(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_dir)
            path = os.path.join(project_root, "data/database", "assets.json")
            
            if not os.path.exists(path):
                print(f"[ResourceManager] WARNING: Manifest not found at {path}")
                return

            with open(path, "r") as f:
                data = json.load(f)
                
                categories = ["SPRITES", "ANIMATIONS", "SFX", "AMBIENCE", "MUSIC"]
                for category in categories:
                    if category in data:
                        self.asset_map.update(data[category])
                
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

    def get_sound(self, key_or_path):
        if not key_or_path: return None
        
        real_path = self.asset_map.get(key_or_path, key_or_path)
        
        if real_path in self.sounds:
            return self.sounds[real_path]
            
        try:
            full_path = resource_path(real_path)
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Sound file not found: {full_path}")
                return None
                
            sound = pygame.mixer.Sound(full_path)
            self.sounds[real_path] = sound
            return sound
        except Exception as e:
            print(f"[ResourceManager] Error loading sound '{key_or_path}': {e}")
            return None

    def play_music(self, music_id, volume=0.6, loops=-1, fade_ms=500):
        try:
            real_path = self.asset_map.get(music_id, music_id)
            
            if self.current_music == real_path: return

            full_path = resource_path(real_path)
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Music not found: {full_path}")
                return

            print(f"[ResourceManager] Playing music: {music_id} -> {real_path}")
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            
            self.current_music = real_path
            
        except Exception as e:
            print(f"[ResourceManager] Error music '{music_id}': {e}")
        
    def get_font(self, size):
        if size not in self.fonts:
            try:
                font_path = resource_path("assets/fonts/little-pixel.ttf")
                font = pygame.font.Font(font_path, size)
                self.fonts[size] = font
            except Exception as e:
                print(f"[ResourceManager] Error loading font size {size}: {e}")
                self.fonts[size] = pygame.font.SysFont("Arial", size)
            
        return self.fonts[size]

    def load_images_from_list(self, image_ids):
        loaded_images = []
        for img_id in image_ids:
            img = self.get_image(img_id)
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
        self.images.clear()
        self.sounds.clear()
        print(f"[ResourceManager] Cache cleared.")

resource_manager = ResourceManager()