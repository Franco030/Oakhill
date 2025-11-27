from src.GameState import game_state

class EventManager:
    def __init__(self, action_manager):
        self.action_manager = action_manager
        
        self.is_active = False
        self.is_blocking = False
        self.sequence_queue = []
        self.current_step = None
        self.wait_timer = 0
        self.current_image = None

    def start_sequence(self, sequence_list, blocking=False):
        if not sequence_list: return
        if self.is_active: return
        self.sequence_queue = sequence_list.copy()
        self.is_active = True
        self.is_blocking = blocking
        self.current_image = None
        self._next_step()

    def _next_step(self):
        if not self.sequence_queue:
            self.end_sequence()
            return
        self.current_step = self.sequence_queue.pop(0)
        self._process_current_step()

    def _process_current_step(self):
        step = self.current_step
        action = step.get("action")
        params = step.get("params", "")

        if action == "Wait":
            p = self.action_manager.parse_params(params)
            self.wait_timer = float(p.get("time", 1.0)) * 1000
        else:
            pass 

    # def update(self, delta_time, player, scene):
    #     if not self.is_active: return

    #     if self.current_step and self.current_step.get("action") == "Wait":
    #         self.wait_timer -= delta_time
    #         if self.wait_timer <= 0:
    #             self._next_step()
    #         return None
        
    #     elif self.current_step:
    #         action = self.current_step.get("action")
    #         params = self.current_step.get("params", "")
    #         result = self.action_manager.execute(action, params, player, scene)
    #         self._next_step()
    #         return result

    def update(self, delta_time, player, scene):
        if not self.is_active: return None

        if self.current_step and self.current_step.get("action") == "Wait":
            p = self.action_manager.parse_params(self.current_step.get("params", ""))
            if self.wait_timer <= 0 and p:
                 self.wait_timer = float(p.get("time", 1.0)) * 1000

            self.wait_timer -= delta_time
            if self.wait_timer <= 0:
                self._next_step()
            return None

        elif self.current_step:
            action = self.current_step.get("action")
            params = self.current_step.get("params", "")
            
            result = self.action_manager.execute(action, params, player, scene)
            self._next_step()
            return result 
            
        return None

    def end_sequence(self):
        self.is_active = False
        self.is_blocking = False
        self.current_step = None
        self.current_image = None

    def process_trigger(self, obj, player, scene):
        raw_params = getattr(obj, "trigger_params", getattr(obj, "params", ""))
        params = self.action_manager.parse_params(raw_params)

        if hasattr(obj, "condition") and obj.condition == "IfFlag":
            if not game_state.check_flag(params.get("flag"), params.get("value")):
                return None 

        should_kill = False
        if hasattr(obj, "condition") and obj.condition in ["OnEnter", "IfFlag"] and not hasattr(obj, "interaction_type"):
             should_kill = params.get("kill", True)

        if hasattr(obj, "data") and obj.data.get("scripted_events"):
            sequence = obj.data.get("scripted_events")
            blocking = params.get("blocking", False)
            
            self.start_sequence(sequence, blocking)
            
            if should_kill:
                obj.kill()
            
            return None 

        act = getattr(obj, "trigger_action", getattr(obj, "action", "None"))
        if act and act != "None":
            result = self.action_manager.execute(act, raw_params, player, scene)
            
            if act in ["Teleport", "ChangeLevel"]: 
                should_kill = False
            
            if should_kill:
                obj.kill()

            return result
           
        return None