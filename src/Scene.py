import pygame

class Scene:
    """
    Manages the objects and state of the current game "scene" or zone
    The same Scene object is going to be used to represent the "open world", what diferentiates one scene from another is its location
    You may need to make a new Scene object if you "enter a house", because the house will have a different scenario, different object, different events, etc.
    """
    def __init__(self, initial_location: tuple, obstacles: dict, enemies: dict, map_level):
        """
        Description: Initializes the scene
        Parameters:
            initial_locaiton (tuple): A tuple (x, y) representing the starting zone in the map_level.
            obstacles (dict): A dictionary where keys are zone coordinates and values are a list of _Obstacle objects in the zone
            enemies (dict): A dictionary where keys are zone coordinates and values are a lis of _Enemy objects in the zone
            map_level: The 2D array representing the game map, indicating traversable zones.
        Functionality:
            Initializes _obstacles which is a list of all obstacles in the scene, it will be used to load and draw the obstacles in different locations
            Initializes _interactables which is a kind of obstacles that is interactable e.g. (a door, a tree that has apples in it, a trapdoor, etc.)
        """
        self.location = initial_location
        self.map_level = map_level
        self.enemies_dict = enemies
        self._enemies = pygame.sprite.Group()
        self._enemies.add(enemy for enemy in self.enemies_dict[initial_location])
        self.obstacles_dict = obstacles
        self._obstacles = pygame.sprite.Group()
        self._obstacles.add(obstacle for obstacle in self.obstacles_dict[initial_location])
        self._interactables = pygame.sprite.Group()


    def check_zone(self, cords: tuple):
        """
        Checks if a given zone coordinate (y, x) is accesible on the map_level
        """
        try:
            return self.map_level[cords[0]][cords[1]] == 1
        except IndexError:
            return False
        
    @property
    def obstacles(self):
        return self._obstacles
    
    @property
    def enemies(self):
        return self._enemies
        
    def _load_obstacles_for_current_location(self):
        """
        Clears the current obstacles and loads new ones based on the self.location
        """
        self._obstacles.empty()
        if self.location in self.obstacles_dict:
            self._obstacles.add(obstacle for obstacle in self.obstacles_dict[self.location])

    
    def set_location(self, new_location: tuple):
        """
        Changes the current's scene location and reloads the appropriate obstacles
        """
        if self.location != new_location:
            self.location = new_location
            self._load_obstacles_for_current_location()

    def draw(self, screen, player):
        """
        Draws the obstacles and the player in the correct rendering order (depth sorting)
        Since enemies are ghosts they will always be above everything.
        """
        sprites = list(self._obstacles) + [player.sprite]
        sprites.sort(key=lambda sprite: sprite.rect.bottom)

        for sprite in sprites:
            screen.blit(sprite.image, sprite.rect)

        for enemy in self._enemies:
            screen.blit(enemy.image, enemy.rect)
                