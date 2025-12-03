import pygame
import os
from utils import resource_path

class ResourceManager:
    _fonts = {}


    @staticmethod
    def get_font(size):
        if size not in ResourceManager._fonts:
            try:
                font_path = resource_path("assets/fonts/little-pixel.ttf")
                font = pygame.font.Font(font_path, size)
                ResourceManager._fonts[size] = font
                print(f"[ResourceManager] Loaded Global Font size {size}")
            except Exception as e:
                print(f"[ResourceManager] Error loading font size {size}: {e}")
                ResourceManager._fonts[size] = pygame.font.SysFont("Arial", size)
            
        return ResourceManager._fonts[size]


    @staticmethod
    def load_all_sounds(folder_relative_path):
        sounds = {}
        full_path = resource_path(folder_relative_path)
        
        valid_ext = ('.wav', '.mp3', '.ogg')

        if not os.path.exists(full_path):
            print(f"[ResourceManager] Error: Folder {folder_relative_path} doesn't exist")
            return sounds

        print(f"[ResourceManager] Loading sounds from: {folder_relative_path}...")

        for root, _, files in os.walk(full_path):
            for filename in files:
                if filename.lower().endswith(valid_ext):
                    key_name = os.path.splitext(filename)[0]
                    file_path = os.path.join(root, filename)
                    
                    try:
                        sound = pygame.mixer.Sound(file_path)
                        sounds[key_name] = sound
                        print(f"  -> Loaded: {key_name}")
                    except Exception as e:
                        print(f"  -> Error loading {filename}: {e}")
        
        return sounds
    
    @staticmethod
    def load_all_images(folder_relative_path):
        images = {}
        full_path = resource_path(folder_relative_path)
        valid_ext = ('.png', '.jpg', '.jpeg')

        if not os.path.exists(full_path):
            print(f"[ResourceManager] Error: Folder: {folder_relative_path} doesn't exist")
            return images

        print(f"[ResourceManager] Loading images from: {folder_relative_path}...")

        for root, _, files in os.walk(full_path):
            for filename in files:
                if filename.lower().endswith(valid_ext):
                    key_name = os.path.splitext(filename)[0]
                    file_path = os.path.join(root, filename)
                    
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        images[key_name] = img
                    except Exception as e:
                        print(f"  -> Error loading image {filename}: {e}")
        
        return images
    
    @staticmethod
    def load_images_from_list(file_paths):
        loaded_images = []
        print(f"[RESOURCE MANAGER] Loading batch of {len(file_paths)} images...")

        for path in file_paths:
            full_path = resource_path(path)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                loaded_images.append(img)
            except Exception as e:
                print(f"[RESOURCE MANAGER] Error loading animation frame '{path}': {e}")

            
        return loaded_images
    
    @staticmethod
    def play_music(relative_path, volume=0.6, loops=-1, fade_ms=500):
        try:
            full_path = resource_path(relative_path)
            
            if not os.path.exists(full_path):
                print(f"[ResourceManager] Error: Music file not found at {full_path}")
                return

            print(f"[ResourceManager] Playing music: {relative_path}")
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            
        except Exception as e:
            print(f"[ResourceManager] Critical Error loading music '{relative_path}': {e}")