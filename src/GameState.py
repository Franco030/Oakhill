class GameState:
    """
    Global memory of the game
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance  = super(GameState, cls).__new__(cls)
            cls._instance.flags = {}
        return cls._instance
    
    def set_flag(self, key, value):
        """
        Stores a value (True, False, Number, String)
        """
        self.flags[key] = value
        print(f"[GameState] Flag '{key}' set to {value}" )

    def get_flag(self, key, default=None):
        """
        Gets a value. If not value, returns default
        """
        return self.flags.get(key, default)
    
    def increment_flag(self, key, amount=1):
        """
        Increments a counter (e.g. Read notes)
        """
        current = self.get_flag(key, 0)
        if isinstance(current, (int, float)):
            self.set_flag(key, current + amount)

    def check_flag(self, key, expected_value):
        """
        Compares a flag to an expected_value
        """
        return self.get_flag(key) == expected_value
    
game_state = GameState()