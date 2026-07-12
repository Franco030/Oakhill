import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", message=".*pkg_resources.*")
import pygame
import inspect
from src.scripting.Interpreter import Interpreter

class DebugConsole:
    def __init__(self, game):
        self.game = game
        self.interpreter = Interpreter(game.action_manager, game.player, None)

        self.is_active = False
        self.input_text = ""
        self.history = [] # Logs
        self.history_limit = 10

        self.font = pygame.font.SysFont("Consolas", 14)
        self.height = 300
        self.bg_color = (0, 0, 0, 200)
        self.text_color = (200, 200, 200)
        self.error_color = (255, 0, 0)

        self.cursor_visible = True
        self.cursor_timer = 0

    def toggle(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.input_text = ""
            pygame.key.set_repeat(500, 50)
        else:
            pygame.key.set_repeat(0)

    def log(self, message, is_error=False):
        color = self.error_color if is_error else self.text_color
        self.history.append({"text": str(message), "color": color})
        if len(self.history) > self.history_limit:
            self.history.pop(0)

    def handle_event(self, event):
        if not self.is_active: return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.execute_command()

            elif event.key == pygame.K_BACKQUOTE:
                self.toggle()

            else:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    self.input_text += event.unicode

            return True
        
        return False
    
    def execute_command(self):
        cmd = self.input_text.strip()
        self.log(f"> {cmd}")
        
        if not cmd: return

        try:
            self.interpreter.player = self.game.player
            self.interpreter.scene = self.game.level_manager.current_scene
            
            if hasattr(self.interpreter, 'execute_raw_call'):
                gen = self.interpreter.execute_raw_call(cmd, print_callback=self.log)
                if inspect.isgenerator(gen):
                    self.game.event_manager.start_script(gen)
                elif gen is not None:
                    if isinstance(gen, str) and gen.startswith("Error"):
                        pass # error is already logged by execute_raw_call if print_callback is present, but let's be safe
                    else:
                        self.log(str(gen))
            else:
                self.log("Error: Interpreter missing 'execute_raw_call'", True)

        except Exception as e:
            self.log(f"Sys Error: {e}", True)
        
        self.input_text = ""

    def update(self, delta_time):
        if not self.is_active: return
        self.cursor_timer += delta_time
        if self.cursor_timer >= 500:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        if not self.is_active: return

        s = pygame.Surface((screen.get_width(), self.height))
        s.set_alpha(200)
        s.fill((0,0,0))
        screen.blit(s, (0, 0))

        y_offset = 10
        for entry in self.history:
            text_surf = self.font.render(entry["text"], True, entry["color"])
            screen.blit(text_surf, (10, y_offset))
            y_offset += 20

        pygame.draw.line(screen, (100, 100, 100), (0, self.height - 30), (screen.get_width(), self.height - 30), 1)
        
        prompt = f">> {self.input_text}"
        if self.cursor_visible:
            prompt += "_"
            
        input_surf = self.font.render(prompt, True, (255, 255, 255))
        screen.blit(input_surf, (10, self.height - 25))