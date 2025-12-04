import pygame
from .Game_Constants import *
from .Animations import Animation
from utils import resource_path

class Player(pygame.sprite.Sprite):
    """
    Represents the playable character in the game
    """
    def __init__(self, start_x, start_y, walking_sound=None):
        super().__init__()


        # This is super super super bad, but we'll keep loading this image to get the rectangle right
        # It is not the actual sprite, but since I decided to change the player sprite, no one will notice
        self.image = pygame.image.load(resource_path('assets/images/detective.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * RESIZE_FACTOR, self.image.get_height() * RESIZE_FACTOR))
        self.rect = self.image.get_rect(center = (start_x, start_y))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.prev_pos = self.pos.copy()
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.facing = "down"
        self._collision_rect = pygame.Rect(
            self.rect.left,
            self.rect.top + 45,
            self.rect.width,
            self.rect.height - 80
        )
        self.attack_rect = self.rect.copy()
        self.is_attacking = False
        self.attack_duration = 30
        self.attack_timer = 0
        self.is_defeated = False
        
        self.walking_sound = walking_sound
        self.is_walking_sound_playing = False

        # ---Animations---
        self.animations = {
            'right': Animation(self, [resource_path('assets/animations/walking_right_1.png'), resource_path('assets/animations/walking_right_2.png')], 0.05),
            'left': Animation(self, [resource_path('assets/animations/walking_left_1.png'), resource_path('assets/animations/walking_left_2.png')], 0.05),
            'up': Animation(self, [resource_path('assets/animations/walking_up_1.png'), resource_path('assets/animations/walking_up_2.png')], 0.05),
            'down': Animation(self, [resource_path('assets/animations/walking_down_1.png'), resource_path('assets/animations/walking_down_2.png')], 0.05),

            'attack_down': Animation(self, [resource_path(f"assets/animations/Detective_Att_Bot/detective_att_bot.png")], 0.05),
            'attack_up': Animation(self, [resource_path(f"assets/animations/Detective_Att_Top/detective_att_top.png")], 0.05),
            'attack_left': Animation(self, [resource_path("assets/animations/Detective_Att_Left/detective_att_left.png")], 0.05),
            'attack_right': Animation(self, [resource_path("assets/animations/Detective_Att_Right/detective_att_right.png")], 0.05),

            'defeated': Animation(self, [resource_path("assets/images/detective_dead.png")], 0.05)
        }

    @property
    def collision_rect(self):
        return self._collision_rect

    def cancel_attack(self):
        """
        Interrupts the player's attack
        """
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_rect.width = 0
        self.attack_rect.height = 0

    def attack(self):
        """
        Initiates the player's attack
        """
        if not self.is_attacking and not hasattr(self, 'is_defeated') or not self.is_defeated:
            self.is_attacking = True
            # self.attack_timer = self.attack_duration
            self.direction.x = 0
            self.direction.y = 0

    def defeat(self):
        """
        Handles the player's defeat state
        """
        self.is_defeated = True
        self.direction.x = 0
        self.direction.y = 0
        self.animations['defeated'].animate()

    def reset(self, start_x, start_y):
        """
        Resets the player's state to initial conditions
        """
        self.is_defeated = False
        self.pos = pygame.math.Vector2(start_x, start_y)
        self.collision_rect.center = (start_x, start_y)
        self.facing = "down"
        self.image = self.animations['down'].images[0]
        self.rect = self.image.get_rect(center = self.pos)

        if self.is_walking_sound_playing:
            self.walking_sound.stop()
            self.is_walking_sound_playing = False

    def _handle_walking_sound(self):
        """
        Starts or stops walking sound
        """
        if not self.walking_sound:
            return
        
        is_moving = self.direction.length() > 0 and not self.is_attacking and not self.is_defeated

        if is_moving:
            if not self.is_walking_sound_playing:
                self.walking_sound.play(loops=-1)
                self.is_walking_sound_playing = True
        else:
            if self.is_walking_sound_playing:
                self.walking_sound.stop()
                self.is_walking_sound_playing = False

    def stop_attack(self):
        if self.is_attacking:
            self.is_attacking = False
            self.image = self.animations[self.facing].images[0]

    def _player_input(self):
        """
        Calculates the desired movement direction based on keys pressed
        """

        if self.is_defeated:
            self.animations['defeated'].animate()
            return


        keys = pygame.key.get_pressed()


        if self.is_attacking:
            # self.attack_timer -= 1
            self.animations['attack_' + self.facing].animate()

            RANGE = 250

            if self.facing == "right":
                self.attack_rect = pygame.Rect(
                    self.rect.right,
                    self.rect.top + 10,
                    RANGE,
                    self.rect.height - (self.rect.height / 5)
                )
            elif self.facing == "left":
                self.attack_rect.width = RANGE
                self.attack_rect.height = self.rect.height - (self.rect.height / 5)
                self.attack_rect.right = self.rect.left
                self.attack_rect.top = self.rect.top + 10
            elif self.facing == "up":
                self.attack_rect.width = self.rect.height
                self.attack_rect.height = RANGE - 100
                self.attack_rect.centerx = self.rect.centerx
                self.attack_rect.bottom = self.rect.top
            elif self.facing == "down":
                self.attack_rect.width = self.rect.height
                self.attack_rect.height = RANGE - 100
                self.attack_rect.centerx = self.rect.centerx
                self.attack_rect.top = self.rect.bottom

            # if self.attack_timer <= 0:
            #     self.is_attacking = False
            #     self.attack_rect.width = 0
            #     self.attack_rect.height = 0
            #     self.image = self.animations[self.facing].images[0]

        else:
            self.direction.x = 0
            self.direction.y = 0
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.facing = "up"
                self.animations['up'].animate()
            if keys[pygame.K_s]:
                self.direction.y = 1
                self.facing = "down"
                self.animations['down'].animate()
            if keys[pygame.K_a]:
                self.direction.x = -1
                self.facing = "left"
                self.animations['left'].animate()
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.facing = "right"
                self.animations['right'].animate()
            self.attack_rect.width = 0
            self.attack_rect.height = 0
            
        if self.direction.length() > 0:
            self.direction.normalize_ip()

    def _move_x(self, obstacles):
        """
        Handles horizontal movement and collision detection with obstacles
        """
        self.pos.x += self.velocity.x
        self._collision_rect.centerx = int(self.pos.x)

        for obstacle in obstacles:
            if self._collision_rect.colliderect(obstacle.collision_rect):
                if self.velocity.x > 0:
                    self._collision_rect.right = obstacle.collision_rect.left
                elif self.velocity.x < 0:
                    self._collision_rect.left = obstacle.collision_rect.right

                self.pos.x = self._collision_rect.centerx

    def _move_y(self, obstacles):
        """
        Handles vertical movement and collision detection with obstacles
        """
        self.pos.y += self.velocity.y
        self._collision_rect.centery = int(self.pos.y)

        for obstacle in obstacles:
            if self._collision_rect.colliderect(obstacle.collision_rect):
                if self.velocity.y > 0:
                    self._collision_rect.bottom = obstacle.collision_rect.top
                elif self.velocity.y < 0:
                    self._collision_rect.top = obstacle.collision_rect.bottom

                self.pos.y = self._collision_rect.centery

    def teleport(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        
        self.rect.center = (int(x), int(y))
        
        self._collision_rect.centerx = self.rect.centerx
        
        self._collision_rect.centery = int(self.pos.y)
        
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, 0)

    def update(self, obstacles):
        """
        Updates the player's state based on input and game logic
        """
        self._player_input()

        self.prev_pos = self.pos.copy()
        self.velocity = self.direction * PLAYER_SPEED

        self._handle_walking_sound()

        self._move_x(obstacles)
        self._move_y(obstacles)

        self.rect = self.image.get_rect(center = (int(self.pos.x), int(self.pos.y)))