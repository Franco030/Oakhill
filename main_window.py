import pygame
import sys
import os
from src.Game_Constants import *
from src.Player import Player
from src.Scene_Loader import SceneLoader
from src.ActionManager import ActionManager # <--- NUEVO: El cerebro de eventos
from src.GameState import game_state        # <--- NUEVO: La memoria global

# --- Configuración de Rutas ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Configuración Inicial ---
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Oakhill")

# Cargar Recursos Globales (Fuentes, Sonidos)
try:
    font_path = resource_path("assets/fonts/scary_font.ttf")
    # Sonidos
    chase_sound = pygame.mixer.Sound(resource_path("assets/sounds/chase_loop.wav"))
    flee_sound = pygame.mixer.Sound(resource_path("assets/sounds/flee_loop.wav"))
    note_sound = pygame.mixer.Sound(resource_path("assets/sounds/note_reading.wav"))
    steps_sound = pygame.mixer.Sound(resource_path("assets/sounds/steps_cut.wav"))
    # Ajustar volúmenes
    chase_sound.set_volume(0.4)
    flee_sound.set_volume(0.4)
    note_sound.set_volume(1.0)
    steps_sound.set_volume(0.3)
except Exception as e:
    print(f"Error cargando recursos: {e}")
    # Crear objetos dummy si fallan los sonidos para no crashear
    class DummySound:
        def play(self, loops=0): pass
        def stop(self): pass
        def set_volume(self, v): pass
    chase_sound = flee_sound = note_sound = steps_sound = DummySound()

# --- Funciones de UI ---

def draw_note_ui(screen, note_data):
    """Dibuja la interfaz de lectura de notas."""
    padding = 50
    ui_width = SCREEN_WIDTH - padding * 2
    ui_height = SCREEN_HEIGHT - padding * 2

    # Fondo semitransparente
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    s.set_alpha(180)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))

    # Hoja de papel
    sheet_rect = pygame.Rect(padding, padding, ui_width, ui_height)
    pygame.draw.rect(screen, (20, 20, 20), sheet_rect) # Fondo oscuro
    pygame.draw.rect(screen, (200, 200, 200), sheet_rect, 2) # Borde claro

    try:
        font = pygame.font.Font(font_path, 32)
    except:
        font = pygame.font.SysFont("Arial", 32)

    # Manejar texto (Lista o String)
    lines_to_render = []
    if isinstance(note_data, list):
        lines_to_render = note_data
    elif isinstance(note_data, str):
        lines_to_render = note_data.split('\n')
    
    # Renderizar texto
    line_spacing = 40
    start_x = padding + 40
    start_y = padding + 40

    for i, line in enumerate(lines_to_render):
        render_line = line if line else " "
        text_surface = font.render(render_line, True, (220, 220, 220))
        screen.blit(text_surface, (start_x, start_y + i * line_spacing))

    # Instrucción de cerrar
    try:
        close_font = pygame.font.Font(None, 24)
    except:
        close_font = pygame.font.SysFont("Arial", 24)
        
    close_text = close_font.render("Presiona 'ESPACIO' para cerrar", True, (150, 150, 150))
    close_rect = close_text.get_rect(centerx = sheet_rect.centerx, bottom = sheet_rect.bottom - 20)
    screen.blit(close_text, close_rect)

def draw_image_ui(screen, image_path):
    """Muestra una imagen en pantalla completa (ej: foto encontrada)."""
    if not image_path or image_path == "None": return

    try:
        full_path = resource_path(image_path)
        if not os.path.exists(full_path): return
        
        img = pygame.image.load(full_path).convert_alpha()
        
        # Fondo oscuro
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        
        # Centrar imagen
        img_rect = img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        # Escalar si es muy grande
        if img_rect.width > SCREEN_WIDTH - 100 or img_rect.height > SCREEN_HEIGHT - 100:
            # Lógica simple de escalado (se puede mejorar)
            scale = min((SCREEN_WIDTH - 100)/img_rect.width, (SCREEN_HEIGHT - 100)/img_rect.height)
            new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
            img = pygame.transform.scale(img, new_size)
            img_rect = img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
        screen.blit(img, img_rect)
        
    except Exception as e:
        print(f"Error mostrando imagen UI: {e}")

# --- Bucle Principal ---

def game_loop(screen, clock):
    # 1. Inicializar Jugador
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # 2. Cargar Escena Inicial
    # Asegúrate de que tu JSON tenga esta estructura o ajusta la ruta
    json_path = resource_path("data/scene_output_new.json") 
    map_level_placeholder = [[1]*10 for _ in range(10)] # Mapa dummy si no tienes uno real aun
    
    scene = SceneLoader.load_from_json(
        json_path, 
        map_level_placeholder, 
        (5, 2), # Zona inicial
        player, 
        chase_sound, 
        flee_sound
    )

    # 3. Inicializar ActionManager (El sistema de eventos)
    action_manager = ActionManager()

    # Variables de Estado del Bucle
    running = True
    game_state_status = "PLAYING" # PLAYING, READING_NOTE, VIEWING_IMAGE
    note_content = []
    image_content = ""
    
    key_pressed_space = False # Debounce para tecla espacio

    while running:
        delta_time = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "QUIT"

        # --- ESTADO: JUGANDO ---
        if game_state_status == "PLAYING":
            
            # 1. Movimiento Jugador
            # Pasamos _obstacles para colisiones físicas
            player.update(scene._obstacles) 
            
            # 2. IA Enemigos
            scene._enemies.update(delta_time)
            
            # 3. Animaciones de Entorno
            scene._obstacles.update()     # Animar árboles, agua, etc.
            scene._interactables.update() # Animar notas brillantes, etc.

            # --- LÓGICA DE TRIGGERS (Invisible) ---
            # Detectar si el jugador pisa un Trigger (OnEnter)
            hit_triggers = pygame.sprite.spritecollide(player.sprite, scene._triggers, False)
            for trig in hit_triggers:
                # Verificar triggers condicionales (IfFlag)
                if trig.condition == "IfFlag":
                    # Parsear params para ver qué flag revisar
                    params = action_manager.parse_params(trig.params)
                    flag_name = params.get("flag")
                    needed_val = params.get("value")
                    
                    if game_state.check_flag(flag_name, needed_val):
                         action_manager.execute(trig.action, trig.params, player, scene)
                         # Opcional: trig.kill() si es de un solo uso

                # Verificar triggers normales de entrada
                elif trig.condition == "OnEnter":
                    action_manager.execute(trig.action, trig.params, player, scene)


            # --- LÓGICA DE INTERACCIÓN (Espacio) ---
            if keys[pygame.K_SPACE] and not key_pressed_space:
                key_pressed_space = True
                
                # Detectar interactuables cercanos (usando attack_rect del jugador)
                # Nota: Usamos .rect para interacción, no collision_rect
                collided_int = pygame.sprite.spritecollide(
                    player.sprite, 
                    scene._interactables, 
                    False, 
                    lambda spr, obj: spr.attack_rect.colliderect(obj.rect)
                )

                if collided_int:
                    obj = collided_int[0] # Tomar el primero
                    
                    # A. Ejecutar Acción Genérica (ActionManager)
                    # Si el objeto tiene configurada una acción en el editor (ej: SetFlag)
                    if hasattr(obj, "data"): # Asegurarnos que tiene datos
                        trig_action = obj.data.get("trigger_action")
                        trig_params = obj.data.get("trigger_params")
                        
                        # Solo ejecutar si la condición es OnInteract o no tiene condición (default)
                        cond = obj.data.get("trigger_condition", "OnInteract")
                        if cond == "OnInteract" and trig_action and trig_action != "None":
                             action_manager.execute(trig_action, trig_params, player, scene)

                    # B. Lógica Específica (Notas / Imágenes / Puertas)
                    # 1. NOTAS
                    if obj.interaction_type == "Note":
                        note_content = obj.interaction_data
                        game_state_status = "READING_NOTE"
                        note_sound.play()
                        obj.interact() # Marcar como leído

                    # 2. IMÁGENES
                    elif obj.interaction_type == "Image":
                        image_content = obj.interaction_data
                        game_state_status = "VIEWING_IMAGE"
                        note_sound.play() # Reusar sonido o poner otro
                        obj.interact()

                    # 3. PUERTAS (Ejemplo simple)
                    elif obj.interaction_type == "Door":
                        # Aquí podrías checar una flag antes de abrir
                        # if game_state.get_flag("has_key"): ...
                        print("Es una puerta.")

            if not keys[pygame.K_SPACE]:
                key_pressed_space = False

            # --- DIBUJADO ---
            screen.fill((0, 0, 0)) # Limpiar pantalla
            
            # La escena se encarga de dibujar en orden (Suelo -> Z -> Y)
            scene.draw(screen, player)
            
            # Dibujar HUD o efectos globales aquí si los hubiera

        # --- ESTADO: LEYENDO NOTA ---
        elif game_state_status == "READING_NOTE":
            # Dibujar el juego de fondo congelado
            scene.draw(screen, player)
            
            # Dibujar UI
            draw_note_ui(screen, note_content)

            # Salir al presionar espacio
            if keys[pygame.K_SPACE] and not key_pressed_space:
                key_pressed_space = True
                game_state_status = "PLAYING"
            
            if not keys[pygame.K_SPACE]:
                key_pressed_space = False

        # --- ESTADO: VIENDO IMAGEN ---
        elif game_state_status == "VIEWING_IMAGE":
            scene.draw(screen, player)
            draw_image_ui(screen, image_content)

            if keys[pygame.K_SPACE] and not key_pressed_space:
                key_pressed_space = True
                game_state_status = "PLAYING"
            
            if not keys[pygame.K_SPACE]:
                key_pressed_space = False

        # Actualizar pantalla
        pygame.display.flip()

    return "QUIT"

def main():
    clock = pygame.time.Clock()
    game_loop(screen, clock)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()