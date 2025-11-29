# import pygame
# import random
# from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT

# class RetroEffects:
#     def __init__(self):
#         self.scanline_offset = 0
#         self.scanline_speed = 0.01
#         self.flicker_timer = 0
#         self.noise_line_y = -100
#         self.noise_timer = 0
        
#         self.scanlines_surf = self._create_scanlines()
#         self.vignette_surf = self._create_vignette()
#         self.noise_surf = self._create_noise_texture()

#         self.grain_timer = 0
#         self.grain_offset = (0, 0)

#     def _create_scanlines(self):
#         surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + 10))
#         surf.set_colorkey((0, 0, 0))
#         surf.fill((0, 0, 0))

#         line_color = (20, 20, 20)

#         for y in range(0, SCREEN_HEIGHT + 10, 4):
#             pygame.draw.line(surf, line_color, (0, y), (SCREEN_WIDTH, y), 1)

#         surf.set_alpha(50)
#         return surf
    
#     def _create_vignette(self):
#         surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
#         surf.fill((0, 0, 0, 0)) # Transparente total
        
#         max_radius = int(((SCREEN_WIDTH/2)**2 + (SCREEN_HEIGHT/2)**2)**0.5)
#         center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
#         for r in range(max_radius, int(SCREEN_HEIGHT * 0.4), -8):
#             progress = (r - (SCREEN_HEIGHT * 0.4)) / (max_radius - (SCREEN_HEIGHT * 0.4))
#             alpha = int(min(255, progress * 200))
            
#             pygame.draw.circle(surf, (0, 0, 0, alpha), center, r, 10)
            
#         return surf
    
#     def _create_noise_texture(self):
#         w, h = 256, 256
#         surf = pygame.Surface((w, h), pygame.SRCALPHA)

#         for _ in range(2000):
#             x = random.randint(0, w-1)
#             y = random.randint(0, h-1)
#             alpha = random.randint(5, 10)
#             surf.set_at((x, y), (10, 10, 10, alpha))
            
#         return surf
    
#     def update_and_draw(self, screen, delta_time):
#         self.grain_timer += delta_time
#         if self.grain_timer > 30:
#             self.grain_offset = (random.randint(-100, 0), random.randint(-100, 0))
#             self.grain_timer = 0
            

#         for x in range(self.grain_offset[0], SCREEN_WIDTH, 256):
#             for y in range(self.grain_offset[1], SCREEN_HEIGHT, 256):
#                 screen.blit(self.noise_surf, (x, y), special_flags=pygame.BLEND_ADD)

#         self.scanline_offset = (self.scanline_offset + self.scanline_speed) % 4
        
#         self.flicker_timer += delta_time
#         if self.flicker_timer > 50:
#             new_alpha = random.randint(100, 140)
#             self.scanlines_surf.set_alpha(new_alpha)
#             self.flicker_timer = 0

#         screen.blit(self.scanlines_surf, (0, -int(self.scanline_offset)))

#         self.noise_timer -= delta_time
#         if self.noise_timer <= 0:
#             self.noise_line_y = random.randint(0, SCREEN_HEIGHT // 2)
#             self.noise_timer = random.randint(20000, 30000)
        
#         if self.noise_line_y < SCREEN_HEIGHT:
#             height = random.randint(5, 20)
#             noise_rect = pygame.Rect(0, self.noise_line_y, SCREEN_WIDTH, height)
#             shape_surf = pygame.Surface(noise_rect.size, pygame.SRCALPHA)
#             shape_surf.fill((50, 50, 50, 100))
#             screen.blit(shape_surf, noise_rect, special_flags=pygame.BLEND_ADD)
#             self.noise_line_y += 5


#             offset_x = random.randint(-20, 20) 
            
#             # Evitamos que el offset sea 0 (porque entonces no se vería nada)
#             if offset_x == 0: offset_x = 5

#             screen.blit(screen, (offset_x, self.noise_line_y), area=noise_rect)
            
#             tint_surf = pygame.Surface(noise_rect.size)
#             tint_surf.fill((0, 10, 10))
#             screen.blit(tint_surf, (offset_x, self.noise_line_y), special_flags=pygame.BLEND_ADD)


#         screen.blit(self.vignette_surf, (0, 0))

import pygame
import random
import math
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT

class RetroEffects:
    def __init__(self):
        # --- SCANLINES ---
        self.scanline_offset = 0
        # Tu preferencia era 0.01. Usaremos esto como base para la oscilación.
        self.scanline_base_speed = 0.02 
        
        # --- FLICKER ---
        self.flicker_timer = 0
        
        # --- INTERFERENCIA (NUEVO SISTEMA DE LISTA) ---
        self.active_noises = [] # Lista para múltiples barras
        self.noise_timer = 0    
        
        # --- GRAIN ---
        self.grain_timer = 0
        self.grain_offset = (0, 0)
        
        # --- Generar superficies con tus preferencias ---
        self.scanlines_surf = self._create_scanlines()
        self.vignette_surf = self._create_vignette()
        self.noise_surf = self._create_noise_texture()

    def _create_scanlines(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT + 10))
        surf.set_colorkey((0, 0, 0))
        surf.fill((0, 0, 0))
        
        # Tu color preferido
        line_color = (20, 20, 20) 

        for y in range(0, SCREEN_HEIGHT + 10, 4):
            pygame.draw.line(surf, line_color, (0, y), (SCREEN_WIDTH, y), 1)

        # Tu alpha preferido
        surf.set_alpha(50)
        return surf
    
    def _create_vignette(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) 
        
        max_radius = int(((SCREEN_WIDTH/2)**2 + (SCREEN_HEIGHT/2)**2)**0.5)
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        for r in range(max_radius, int(SCREEN_HEIGHT * 0.4), -8):
            progress = (r - (SCREEN_HEIGHT * 0.4)) / (max_radius - (SCREEN_HEIGHT * 0.4))
            alpha = int(min(255, progress * 120))
            pygame.draw.circle(surf, (0, 0, 0, alpha), center, r, 10)
            
        return surf
    
    def _create_noise_texture(self):
        w, h = 256, 256
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Tus preferencias de Grano: 2000 puntos, muy oscuros y sutiles
        for _ in range(2000):
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            alpha = random.randint(5, 10)
            surf.set_at((x, y), (10, 10, 10, alpha))
            
        return surf
    
    def _spawn_noise_bar(self):
        """Genera una barra con tus preferencias de velocidad y tamaño"""
        direction = random.choice([-1, 1]) # Puede ir arriba o abajo
        
        # Tu velocidad preferida era 5. Hacemos que varíe ligeramente alrededor de 5.
        base_speed = 5
        speed = random.randint(base_speed - 1, base_speed + 2) * direction
        
        # Altura variable (5 a 20 como tenías antes)
        height = random.randint(5, 20)
        
        if direction == 1:
            start_y = -height
        else:
            start_y = SCREEN_HEIGHT
            
        return {
            'y': start_y,
            'height': height,
            'speed': speed
        }

    def update_and_draw(self, screen, delta_time):
        # 1. RUIDO DE GRANO (GRAIN)
        self.grain_timer += delta_time
        if self.grain_timer > 30:
            self.grain_offset = (random.randint(-100, 0), random.randint(-100, 0))
            self.grain_timer = 0
            
        for x in range(self.grain_offset[0], SCREEN_WIDTH, 256):
            for y in range(self.grain_offset[1], SCREEN_HEIGHT, 256):
                # Mantengo tu preferencia de BLEND_ADD
                screen.blit(self.noise_surf, (x, y), special_flags=pygame.BLEND_ADD)

        # 2. SCANLINES DINÁMICAS (Lentas como te gustan)
        # Usamos oscilación suave pero mantenemos la velocidad base muy baja
        current_time = pygame.time.get_ticks() / 1000.0
        oscillation = math.sin(current_time * 0.5) * 0.02 # Variación muy pequeña
        
        # La velocidad oscilará cerca de tu 0.01 original
        current_speed = self.scanline_base_speed + oscillation
        self.scanline_offset = (self.scanline_offset + current_speed) % 4
        
        # Flicker (Mismo rango 100-140 que tenías)
        self.flicker_timer += delta_time
        if self.flicker_timer > 50:
            new_alpha = random.randint(100, 140)
            self.scanlines_surf.set_alpha(new_alpha)
            self.flicker_timer = 0

        screen.blit(self.scanlines_surf, (0, -int(self.scanline_offset)))

        # 3. INTERFERENCIA MÚLTIPLE
        self.noise_timer -= delta_time
        if self.noise_timer <= 0:
            # A veces sale 1, a veces 2 barras
            num_bars = random.choices([1, 2], weights=[0.8, 0.2])[0]
            for _ in range(num_bars):
                self.active_noises.append(self._spawn_noise_bar())
            
            # Tu rango de tiempo preferido: 20s a 30s
            self.noise_timer = random.randint(20000, 30000)
        
        # Actualizar y dibujar lista de barras
        remaining_noises = []
        
        for noise in self.active_noises:
            noise['y'] += noise['speed']
            
            # Solo dibujamos si está en pantalla (con margen)
            if -50 < noise['y'] < SCREEN_HEIGHT + 50:
                noise_rect = pygame.Rect(0, int(noise['y']), SCREEN_WIDTH, noise['height'])
                
                # Tu color de barra preferido (50, 50, 50, 100)
                shape_surf = pygame.Surface(noise_rect.size, pygame.SRCALPHA)
                shape_surf.fill((50, 50, 50, 100))
                screen.blit(shape_surf, noise_rect, special_flags=pygame.BLEND_ADD)
                
                # Efecto TEARING con tu configuración (-20, 20)
                offset_x = random.randint(-20, 20)
                if offset_x == 0: offset_x = 5
                
                screen.blit(screen, (offset_x, int(noise['y'])), area=noise_rect)
                
                # Tu Tinte Cian Oscuro (0, 10, 10)
                tint_surf = pygame.Surface(noise_rect.size)
                tint_surf.fill((0, 10, 10))
                screen.blit(tint_surf, (offset_x, int(noise['y'])), special_flags=pygame.BLEND_ADD)
                
                remaining_noises.append(noise)
        
        self.active_noises = remaining_noises

        # 4. VIÑETA
        screen.blit(self.vignette_surf, (0, 0))