class TweenManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TweenManager, cls).__new__(cls)
            cls._instance.active_tweens = []
        return cls._instance
    
    def teleport(self, obj, target_x, target_y, relative=False):
        current_x = obj.rect.x
        current_y = obj.rect.y
        if hasattr(obj, 'x'): current_x = obj.x
        if hasattr(obj, 'y'): current_y = obj.y

        final_x = target_x
        final_y = target_y

        if relative:
            final_x = current_x + target_x
            final_y = current_y + target_y

        self._apply_to_object(obj, final_x, final_y)
        
        print(f"[TweenManager] Teleported object to ({final_x}, {final_y})")

    def start_move(self, obj, target_x, target_y, duration, relative=False, on_complete=None):
        start_x = obj.rect.x
        start_y = obj.rect.y
        
        if hasattr(obj, 'x'): start_x = obj.x
        if hasattr(obj, 'y'): start_y = obj.y

        final_x = target_x
        final_y = target_y

        if relative:
            final_x = start_x + target_x
            final_y = start_y + target_y

        tween = {
            "obj": obj,
            "start_x": start_x,
            "start_y": start_y,
            "end_x": final_x,
            "end_y": final_y,
            "duration": float(duration) if duration > 0 else 0.001,
            "elapsed": 0.0,
            "finished": False,
            "on_complete": on_complete
        }
        
        self.active_tweens.append(tween)
        print(f"[TweenManager] Started moving object to ({final_x}, {final_y})")

    def update(self, delta_time):
        for tween in self.active_tweens[:]:
            tween["elapsed"] += delta_time
            
            progress = tween["elapsed"] / tween["duration"]
            if progress >= 1.0:
                progress = 1.0
                tween["finished"] = True
            
            # Linear movement, I may use other types of movement later

            current_x = tween["start_x"] + (tween["end_x"] - tween["start_x"]) * progress
            current_y = tween["start_y"] + (tween["end_y"] - tween["start_y"]) * progress
            
            self._apply_to_object(tween["obj"], current_x, current_y)
            
            if tween["finished"]:
                if tween.get("on_complete"):
                    tween["on_complete"]()
                self.active_tweens.remove(tween)

    def _apply_to_object(self, obj, x, y):
        if hasattr(obj, 'x'): obj.x = x
        if hasattr(obj, 'y'): obj.y = y
        
        obj.rect.centerx = int(x)
        obj.rect.centery = int(y)
        

        if hasattr(obj, 'data') and isinstance(obj.data, dict):
            obj.data['x'] = int(x)
            obj.data['y'] = int(y)
        

        if hasattr(obj, 'collision_rect'):
            if getattr(obj, 'is_passable', False):
                return
            offset = getattr(obj, 'collision_rect_offset', [0, 0, 0, 0])
            if isinstance(offset, list) and len(offset) >= 2:
                obj.collision_rect.x = obj.rect.x + offset[0]
                obj.collision_rect.y = obj.rect.y + offset[1]
            else:
                obj.collision_rect.centerx = int(x)
                obj.collision_rect.centery = int(y)

    def clear(self):
        self.active_tweens.clear()


tween_manager = TweenManager()