class GameState:
    """
    Global memory of the game
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance  = super(GameState, cls).__new__(cls)
            cls._instance.flags = {}
            cls._instance.interacted_objects = set()
            cls._instance.pending_level_change = None
            cls._instance.teleport_req = None
        return cls._instance
    
    # --- Flag logic ---
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
    
    # --- Interactions memory ---
    def register_interaction(self, obj_id):
        """
        Marks an object as permanently used
        
        :param obj_id: Object ID
        """
        self.interacted_objects.add(obj_id)

    def has_interacted(self, obj_id):
        """
        Searchs if the object has been already interacted
        
        :param obj_id: Objects ID
        """
        return obj_id in self.interacted_objects
    
    # --------------------------------------------------

    # --- Change level logic ---
    def request_level_change(self, json_path, map_matrix, entry_zone, player_pos, music_path, darkness):
        """
        Requests main_window to change level in the next frame
        """
        self.pending_level_change = {
            "json_path": json_path,
            "map_matrix": map_matrix,
            "entry_zone": entry_zone,
            "player_pos": player_pos,
            "music_path": music_path,
            "darkness": darkness
        }

    def consume_level_change(self):
        """
        Returns the request and cleans the variable
        """
        data = self.pending_level_change
        self.pending_level_change = None
        return data
    # ----------------------------------

    # --- Teleport logic ---
    def request_teleport(self, zone_str, x, y):
        self.teleport_req = {
            "zone": zone_str,
            "x": x,
            "y": y
        }

    def consume_teleport(self):
        data = self.teleport_req
        self.teleport_req = None
        return data
    # ------------------------------------------------
    
    def reset(self):
        """
        Deletes all memory to initiate another game
        """
        self.flags = {}
        self.interacted_objects = set()
        self.pending_level_change = None
        self.teleport_req = None
        print("[GameState] Memory restarted (Reset)")
    
game_state = GameState()