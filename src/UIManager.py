import pygame
from utils import resource_path
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ResourceManager import ResourceManager

class UIManager:
    def __init__(self):
        self.active = False
        self.content_type = None # "NOTE" o "IMAGE" o "Animation"
        self.content_data = None
        self.is_blocking = False

        self.font = ResourceManager.get_font(24)
        self.ui_font = ResourceManager.get_font(20)

        self.anim_frames = []
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.1

        
        

    def show_note(self, text, blocking=False):
        self.active = True
        self.is_blocking = blocking
        self.content_type = "NOTE"
        self.content_data = text

    def show_dialogue(self, data, blocking=False):
        self.active = True
        self.is_blocking = blocking 
        self.content_type = "DIALOGUE"
        self.content_data = data # data is a dict, we may use data: dict but meh

    def show_image(self, image_path, blocking=False):
        self.active = True
        self.is_blocking = blocking
        self.content_type = "IMAGE"
        self.content_data = image_path

    def show_animation(self, image_paths, speed=0.1, blocking=False, loop=True):
        self.anim_frames = []
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = speed
        self.anim_loop = loop
        self.content_type = "ANIMATION"

        raw_images = ResourceManager.load_images_from_list(image_paths)

        if raw_images:
            for img in raw_images:
                if img: 
                    scaled = self._scale_surface(img)
                    self.anim_frames.append(scaled)
        
        if len(self.anim_frames) > 0:
            self.active = True
            self.is_blocking = blocking
        else:
            print(f"[UI] Error: No valid frames for animation.")
            self.active = False
            self.is_blocking = False


    # Only for animation
    def update(self, delta_time):
        if not self.active or self.content_type != "ANIMATION" or not self.anim_frames:
            return

        dt_seconds = delta_time / 1000.0
        self.anim_timer += dt_seconds

        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            if self.anim_loop:
                self.anim_index = (self.anim_index + 1) % len(self.anim_frames)
            else:
                if self.anim_index < len(self.anim_frames) - 1:
                    self.anim_index += 1

    def close(self):
        self.active = False
        self.content_type = None
        self.content_data = None
        self.is_blocking = False
        pygame.mixer.music.unpause()

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                self.close()
                return True
        
        return self.is_blocking

    def draw(self, screen):
        if not self.active: return

        if self.content_type == "NOTE":
            self._draw_note(screen)
        elif self.content_type == "DIALOGUE":
            self._draw_dialogue(screen)
        elif self.content_type == "IMAGE":
            self._draw_image(screen)
        elif self.content_type == "ANIMATION":
            self._draw_animation(screen)

    def _scale_surface(self, surface):
        img_rect = surface.get_rect()
        margin = 50
        available_w = SCREEN_WIDTH - (margin * 2)
        available_h = SCREEN_HEIGHT - (margin * 2)

        scale = min(available_w / img_rect.width, available_h / img_rect.height)
        new_size = (int(img_rect.width * scale), int(img_rect.height * scale))

        return pygame.transform.scale(surface, new_size)

    def _draw_note(self, screen):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        padding = 50
        ui_width = SCREEN_WIDTH - padding * 2
        ui_height = SCREEN_HEIGHT - padding * 2
        sheet_rect = pygame.Rect(padding, padding, ui_width, ui_height)
        
        pygame.draw.rect(screen, (0, 0, 0), sheet_rect)
        pygame.draw.rect(screen, (50, 50, 50), sheet_rect, 3)

        lines = self.content_data.split('\n') if isinstance(self.content_data, str) else self.content_data
        start_y = padding + 20
        
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (70, 70, 70))
            screen.blit(txt, (padding + 20, start_y + i * 40))

        close_txt = self.ui_font.render("Presiona 'ESPACIO' para cerrar", True, (200, 200, 200))
        rect = close_txt.get_rect(centerx=sheet_rect.centerx, bottom=sheet_rect.bottom - 20)
        screen.blit(close_txt, rect)

    def _draw_dialogue(self, screen):
        margin = 20
        height = 200
        rect_x = margin
        rect_y = SCREEN_HEIGHT - height - margin
        rect_w = SCREEN_WIDTH - (margin * 2)
        
        box_rect = pygame.Rect(rect_x, rect_y, rect_w, height)
        
        s = pygame.Surface((rect_w, height))
        # s.set_alpha(220)
        s.fill((0, 0, 0))
        screen.blit(s, (rect_x, rect_y))
        
        data = self.content_data
        text_color = data.get("color", (255, 255, 255))
        
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 3) 

        text = data.get("text", "")
        text_start_y = rect_y + 30
        
        lines = text.split('\n') if isinstance(text, str) else [str(text)]
        
        for i, line in enumerate(lines):
            txt_surf = self.ui_font.render(line, True, text_color)
            screen.blit(txt_surf, (rect_x + 30, text_start_y + i * 35))

        close_txt = self.ui_font.render("SPACEBAR", True, (150, 150, 150))
        close_rect = close_txt.get_rect(bottomright=(rect_x + rect_w - 20, rect_y + height - 20))
        screen.blit(close_txt, close_rect)

    def _draw_image(self, screen):
        screen.fill((0, 0, 0))
        try:
            path = resource_path(self.content_data)
            img = pygame.image.load(path).convert_alpha()
            
            img_rect = img.get_rect()
            
            margin = 50 
            available_w = SCREEN_WIDTH - (margin * 2)
            available_h = SCREEN_HEIGHT - (margin * 2)
            
            scale_w = available_w / img_rect.width
            scale_h = available_h / img_rect.height
            
            scale = min(scale_w, scale_h)
            
            new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
            img = pygame.transform.scale(img, new_size)
            
            img_rect = img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(img, img_rect)
            
        except Exception as e:
            print(f"Error UI image: {e}")

        close_txt = self.ui_font.render("Presiona 'ESPACIO' para cerrar", True, (200, 200, 200))
        rect = close_txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT - 20)
        screen.blit(close_txt, rect)

    def _draw_animation(self, screen):
        screen.fill((0, 0, 0))
        if not self.anim_frames: return
        current_img = self.anim_frames[self.anim_index]
        img_rect = current_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(current_img, img_rect)

        # close_txt = self.ui_font.render("Presiona 'ESPACIO' para cerrar", True, (200, 200, 200))
        # rect = close_txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT - 20)
        # screen.blit(close_txt, rect)

    @staticmethod
    def draw_game_over(screen, image):
        if image:
            img_rect = image.get_rect()

            scale_w = SCREEN_WIDTH / img_rect.width
            scale_h = SCREEN_HEIGHT / img_rect.height
            scale = min(scale_w, scale_h)
            
            new_width = int(img_rect.width * scale)
            new_height = int(img_rect.height * scale)
            
            
            scaled = pygame.transform.scale(image, (new_width, new_height))
  
            screen.fill((0,0,0))
 
            rect = scaled.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(scaled, rect)
        else:
            screen.fill((0,0,0))
        
        font = pygame.font.Font(None, 30)
        txt = font.render("Presiona 'ESC' para reiniciar", True, (200, 200, 200))
        screen.blit(txt, txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT-20))