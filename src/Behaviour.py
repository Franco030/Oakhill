import random
import pygame
import math
from src.Game_Constants import SCREEN_HEIGHT, SCREEN_WIDTH, TRANSITION_BIAS
from abc import ABC, abstractmethod

class _Behaviour(ABC):
    """
    Abstract class for all enemy behaviours
    Defines the interface for applying a behaviour to an enemy
    """
    
    @abstractmethod
    def apply(self, enemy, delta_time):
        """
        Applies this behaviour to the given enemy
        Subclasses must implement this method
        Parameterers:
            enemy: The Enemy instance to apply this behaviour to (no longer in use)
            delta_time: Time elapsed since the last update (for frame-rate independence)
        """
        pass


class Sine_Wave_Movement(_Behaviour):
    """
    A behaviour that makes the enemy move in a sine wave pattern vertically
    """
    def __init__(self, amplitude=70, frequency=0.5, x_velocity = 1, direction = True):
        self.amplitude = amplitude
        self.frequency = frequency
        self.x_velocity = x_velocity
        self.direction = direction
        self.time_ellapsed = 0.0

    def apply(self, enemy, delta_time):
        self.time_ellapsed += delta_time / 1000.0

        enemy.y_offset = self.amplitude * math.sin(self.time_ellapsed * self.frequency * 2 * math.pi)
        if self.direction:
            enemy.x_offset += self.x_velocity
        else:
            enemy.x_offset -= self.x_velocity

    def reverse(self):
        """
        Reverses the horizontal movement direction
        """
        self.direction = not self.direction


class StalkerBehaviour(_Behaviour):
    """
    A behaviour that makes the enemy follow the player
    """
    def __init__(self, target, speed, min_wait=5.0, max_wait=15.0, stop_distance=50, chase_sound=None, flee_sound=None):
        self.target = target
        self.speed = speed
        self.flee_speed = speed * 1.5
        self.stop_distance = stop_distance
        self.min_wait = min_wait
        self.max_wait = max_wait

        # State variables
        self.state = "WAITING"
        self.timer = 0.0
        self.current_wait_time = random.uniform(self.min_wait, self.max_wait)
        self.flee_target = pygame.math.Vector2()

        self.chase_sound = chase_sound
        self.is_chase_sound_playing = False
        self.flee_sound = flee_sound

    def _start_waiting_offscreen(self, enemy):
        """
        Random Spawn offscreen logic
        """
        self.state = "WAITING"
        self.timer = 0.0
        self.current_wait_time = random.uniform(self.min_wait, self.max_wait)

        side = random.randint(0, 3)

        if side == 0: # Top
            enemy.x = random.randint(0, SCREEN_WIDTH)
            enemy.y = -300 - TRANSITION_BIAS # offscreen
        elif side == 1: # Right
            enemy.x = SCREEN_WIDTH + 300 + TRANSITION_BIAS # offscreen
            enemy.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2: # Bottom
            enemy.x = random.randint(0, SCREEN_WIDTH)
            enemy.y = SCREEN_HEIGHT + 300 + TRANSITION_BIAS # offscreen
        else: # Left
            enemy.x = -300 - TRANSITION_BIAS # offscreen
            enemy.y = random.randint(0, SCREEN_HEIGHT)

    def _stop_chase_sound(self):
        """
        Stops chase sound
        """
        if self.chase_sound and self.is_chase_sound_playing:
            self.chase_sound.stop()
            self.is_chase_sound_playing = False

    def apply(self, enemy, delta_time):
        dt_sec = delta_time / 1000.0

        if self.state == "WAITING":
            # Waiting state
            self._stop_chase_sound()
            if self.target.is_defeated:
                return

            self.timer += dt_sec
            if self.timer >= self.current_wait_time:
                self.state = "PURSUING"
                self.timer = 0.0
        elif self.state == "PURSUING":
            # Pursuing state

            if self.chase_sound and not self.is_chase_sound_playing:
                self.chase_sound.play(loops=-1)
                self.is_chase_sound_playing = True
            direction = pygame.Vector2(self.target.rect.centerx - enemy.x, self.target.rect.centery - enemy.y)
            distance = direction.length()

            if distance > self.stop_distance:
                # Keep moving towards the target
                direction.normalize_ip()
                enemy.x += direction.x * self.speed * dt_sec
                enemy.y += direction.y * self.speed * dt_sec

                # Reset offsets
                enemy.x_offset = 0
                enemy.y_offset = 0
            else:
                # Arrived
                self.state = "ARRIVED"
        elif self.state == "ARRIVED":
            # Arrived state
            self._stop_chase_sound()
        elif self.state == "FLEEING":
            self._stop_chase_sound()
            direction = pygame.math.Vector2(self.flee_target.x - enemy.x, self.flee_target.y - enemy.y)
            distance = direction.length()
            if distance > 10:
                direction.normalize_ip()
                enemy.x += direction.x * self.flee_speed * dt_sec
                enemy.y += direction.y * self.flee_speed * dt_sec
            else:
                self._start_waiting_offscreen(enemy)
    
    def shoo(self, enemy):
        """
        The player will call this when attacking
        """
        if self.state == "FLEEING":
            return # Already fleeing
        
        self.state = "FLEEING"
        self._stop_chase_sound()
        if self.flee_sound:
            self.flee_sound.play()

        dist_top = enemy.y
        dist_bottom = SCREEN_HEIGHT - enemy.y
        dist_left = enemy.x
        dist_right = SCREEN_WIDTH - enemy.x

        min_dist = min(dist_top, dist_bottom, dist_left, dist_right)


        # Flee target calculation
        if min_dist == dist_top:
            self.flee_target.x = enemy.x
            self.flee_target.y = -100 
        elif min_dist == dist_bottom:
            self.flee_target.x = enemy.x
            self.flee_target.y = SCREEN_HEIGHT + 100 
        elif min_dist == dist_left:
            self.flee_target.x = -100 
            self.flee_target.y = enemy.y
        else: # dist_right
            self.flee_target.x = SCREEN_WIDTH + 100
            self.flee_target.y = enemy.y

    def reset(self):
        self.state = "WAITING"
        self._stop_chase_sound()
        print("Stalker reset")


class Do_Nothing_Behaviour(_Behaviour):
    """
    A behaviour that does nothing
    """
    def apply(self, enemy, delta_time):
        pass