import pygame
from utils import resource_path
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT

class UIManager:
    def __init__(self):
        self.active = False
        self.content_type = None # "NOTE" o "IMAGE"
        self.content_data = None
        
        try:
            self.font_path = resource_path("assets/fonts/scary_font.ttf")
            self.font = pygame.font.Font(self.font_path, 36)
            self.ui_font = pygame.font.Font(None, 30)
        except:
            self.font = pygame.font.SysFont("Arial", 36)
            self.ui_font = pygame.font.SysFont("Arial", 30)

    def show_note(self, text):
        self.active = True
        self.content_type = "NOTE"
        self.content_data = text

    def show_image(self, image_path):
        self.active = True
        self.content_type = "IMAGE"
        self.content_data = image_path

    def close(self):
        self.active = False
        self.content_type = None
        self.content_data = None
        pygame.mixer.music.unpause()

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                self.close()
                return True
        
        return True

    def draw(self, screen):
        if not self.active: return

        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        if self.content_type == "NOTE":
            self._draw_note(screen)
        elif self.content_type == "IMAGE":
            self._draw_image(screen)

    def _draw_note(self, screen):
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

    def _draw_image(self, screen):
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
            
            screen.fill((0, 0, 0))
            img_rect = img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(img, img_rect)
            
        except Exception as e:
            print(f"Error UI image: {e}")

        close_txt = self.ui_font.render("Presiona 'ESPACIO' para cerrar", True, (200, 200, 200))
        rect = close_txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT - 20)
        screen.blit(close_txt, rect)

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