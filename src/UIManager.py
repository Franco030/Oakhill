import pygame
from utils import resource_path
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ResourceManager import resource_manager
from src.GameState import game_state

class UIManager:
    def __init__(self, retro_effects):
        self.active = False
        self.content_type = None # "NOTE" o "IMAGE" o "Animation"
        self.content_data = None
        self.is_blocking = False

        self.resume_music_on_close = False

        self.font = resource_manager.get_font(24)
        self.ui_font = resource_manager.get_font(20)

        self.retro_effects = retro_effects

        self.note_pages = []
        self.current_page = 0

        self.choice_selection = None

        self.anim_frames = []
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.1        

    def show_note(self, note_data, blocking=False):
        self.active = True
        self.is_blocking = blocking
        self.content_type = "NOTE"
        
        self.current_note_data = note_data
        self.note_pages = note_data.get("pages", ["..."])
        self.current_page_index = 0

    def show_dialogue(self, data, blocking=False, resume_music_on_close=False):
        self.active = True
        self.is_blocking = blocking 
        self.content_type = "DIALOGUE"
        self.content_data = data
        self.resume_music_on_close = resume_music_on_close

    def show_choice(self, text, target_flag, blocking=True):
        self.active = True
        self.is_blocking = blocking
        self.content_type = "CHOICE"
        
        self.content_data = {
            "text": text,
            "flag": target_flag
        }
        self.choice_selection = True

    def show_image(self, image_id, blocking=False):
        self.active = True
        self.is_blocking = blocking
        self.content_type = "IMAGE"
        self.content_data = image_id

    def show_animation(self, image_ids, speed=0.1, blocking=False, loop=True):
        self.anim_frames = []
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = speed
        self.anim_loop = loop
        self.content_type = "ANIMATION"

        raw_images = resource_manager.load_images_from_list(image_ids)

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
        if self.resume_music_on_close:
            pygame.mixer.music.unpause()
            self.resume_music_on_close = False

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:

            if self.content_type == "CHOICE":
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    self.choice_selection = True
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    self.choice_selection = False

                elif event.key == pygame.K_SPACE:
                    target_flag = self.content_data.get("flag")
                    if target_flag:
                        game_state.set_flag(target_flag, self.choice_selection)
                        print(f"[UI] Choice selected: {target_flag} = {self.choice_selection}")

                    snd = resource_manager.get_sound("sfx_dialogue_closed")
                    if snd: snd.play()

                    self.close()
                return True
            
            elif self.content_type == "NOTE":
                if event.key == pygame.K_SPACE:
                    self.current_page_index += 1

                    if self.current_page_index >= len(self.note_pages):
                        snd = resource_manager.get_sound("sfx_note_closed")
                        if snd: snd.play()
                        self.close()
                    else:
                        snd = resource_manager.get_sound("sfx_turn_pages")
                        if snd: snd.play()
                        self.retro_effects.add_trauma(0.5)

            elif self.content_type == "DIALOGUE":
                if event.key == pygame.K_SPACE:
                    snd = resource_manager.get_sound("sfx_dialogue_closed")
                    if snd: snd.play()
                    self.close()
                    return True

            else:
                if event.key == pygame.K_SPACE:
                    self.close()
                    return True
        
        return self.is_blocking

    def draw(self, screen):
        if not self.active: return

        if self.content_type == "NOTE":
            self._draw_note(screen)
        elif self.content_type == "DIALOGUE":
            self._draw_dialogue(screen)
        elif self.content_type == "CHOICE":
            self._draw_choice(screen)
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

        if 0 <= self.current_page_index < len(self.note_pages):
            page_content = self.note_pages[self.current_page_index]
        else:
            page_content = ""

        lines = page_content.split('\n')
        start_y = padding + 20
        
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (200, 200, 200)) 
            screen.blit(txt, (padding + 20, start_y + i * 40))

        if self.current_page_index < len(self.note_pages) - 1:
            msg = "Press 'SPACE' to continue..."
        else:
            msg = "Press 'SPACE' to close"

        if len(self.note_pages) > 1:
            page_info = f"{self.current_page_index + 1}/{len(self.note_pages)}"
            page_txt = self.ui_font.render(page_info, True, (150, 150, 150))
            screen.blit(page_txt, (sheet_rect.right - 60, sheet_rect.bottom - 40))

        close_txt = self.ui_font.render(msg, True, (200, 200, 200))
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
        rect_color = text_color

        pygame.draw.rect(screen, rect_color, box_rect, 3) 

        text = data.get("text", "")
        text_start_y = rect_y + 30
        
        lines = text.split('\n') if isinstance(text, str) else [str(text)]
        
        for i, line in enumerate(lines):
            txt_surf = self.ui_font.render(line, True, text_color)
            screen.blit(txt_surf, (rect_x + 30, text_start_y + i * 35))

        close_txt = self.ui_font.render("SPACEBAR", True, (150, 150, 150))
        close_rect = close_txt.get_rect(bottomright=(rect_x + rect_w - 20, rect_y + height - 20))
        screen.blit(close_txt, close_rect)

    def _draw_choice(self, screen):
        margin = 20
        height = 200
        rect_x = margin
        rect_y = SCREEN_HEIGHT - height - margin
        rect_w = SCREEN_WIDTH - (margin * 2)
        
        s = pygame.Surface((rect_w, height))
        s.fill((0, 0, 0))
        screen.blit(s, (rect_x, rect_y))
        pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_w, height), 3)

        text = self.content_data.get("text", "¿?")
        lines = text.split('\n')
        text_start_y = rect_y + 30
        
        for i, line in enumerate(lines):
            txt_surf = self.ui_font.render(line, True, (255, 255, 255))
            screen.blit(txt_surf, (rect_x + 30, text_start_y + i * 35))

        opt_y = rect_y + height - 60
        opt_center_x = SCREEN_WIDTH // 2
        
        color_yes = (255, 255, 0) if self.choice_selection else (100, 100, 100)
        color_no = (255, 255, 0) if not self.choice_selection else (100, 100, 100)
        
        txt_yes = self.ui_font.render("YES", True, color_yes)
        txt_no = self.ui_font.render("NO", True, color_no)
        
        screen.blit(txt_yes, (opt_center_x - 100, opt_y))
        screen.blit(txt_no, (opt_center_x + 60, opt_y))
        
        cursor_x = (opt_center_x - 130) if self.choice_selection else (opt_center_x + 30)
        txt_cursor = self.ui_font.render(">", True, (255, 255, 0))
        screen.blit(txt_cursor, (cursor_x, opt_y))

    def _draw_image(self, screen):
        screen.fill((0, 0, 0))
        try:
            img = resource_manager.get_image(self.content_data)
            
            if img:
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

        close_txt = self.ui_font.render("Press 'SPACE' to close", True, (200, 200, 200))
        rect = close_txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT - 20)
        screen.blit(close_txt, rect)

    def _draw_animation(self, screen):
        screen.fill((0, 0, 0))
        if not self.anim_frames: return
        current_img = self.anim_frames[self.anim_index]
        img_rect = current_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(current_img, img_rect)

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
        txt = font.render("Press 'ESC' to restart", True, (200, 200, 200))
        screen.blit(txt, txt.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT-20))