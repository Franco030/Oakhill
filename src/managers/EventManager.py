from src.core.GameState import game_state
from src.utils.Game_Enums import Conditions, Actions

class EventManager:
    def __init__(self, action_manager):
        self.action_manager = action_manager
        
        self.is_active = False
        self.is_blocking = False
        
        self.current_sequence = []
        self.step_index = 0
        
        self.wait_timer = 0
        self.current_image = None

        self.current_source_id = None

    def start_sequence(self, sequence_list, blocking=False, source_id=None):
        if not sequence_list: return
        if self.is_active: return
        
        self.current_sequence = sequence_list 
        self.step_index = 0
        
        self.is_active = True
        self.is_blocking = blocking
        self.current_image = None

        self.current_source_id = source_id
        

    def end_sequence(self):
        self.is_active = False
        self.is_blocking = False
        self.current_sequence = []
        self.step_index = 0
        self.current_image = None
        self.current_source_id = None
        
    def update(self, delta_time, player, scene):
        if not self.is_active:
            return None

        if self.wait_timer > 0:
            self.wait_timer -= delta_time
            return None

        if self.step_index >= len(self.current_sequence):
            self.end_sequence()
            return None

        step = self.current_sequence[self.step_index]
        action = step.get("action")
        raw_params = step.get("params", "")

        if action == Actions.WAIT:
            p = self.action_manager.parse_params(raw_params)
            self.wait_timer = float(p.get("time", 1.0)) * 1000
            self.step_index += 1
            return None

        result = self.action_manager.execute(action, raw_params, player, scene, source_id=self.current_source_id)

        if action == Actions.LABEL:
            self.step_index += 1
            return None

        if isinstance(result, dict) and result.get("type") == "Exit":
            self.end_sequence()
            return None

        if isinstance(result, dict) and result.get("type") == "Jump":
            target_label = result.get("target")
            
            if not target_label:
                print(f"[EventManager] Error: Jump without label target.")
                self.step_index += 1
                return None

            found_index = -1
            for i, s in enumerate(self.current_sequence):
                if s.get("action") == Actions.LABEL:
                    p = self.action_manager.parse_params(s.get("params", ""))
                    lbl_id = p.get("id", p.get("name"))
                    if lbl_id == target_label:
                        found_index = i
                        break
            
            if found_index != -1:
                print(f"[EventManager] Jump to '{target_label}' (index {found_index})")
                self.step_index = found_index
            else:
                print(f"[EventManager] ERROR: Label '{target_label}' not found. Continuing")
                self.step_index += 1
            
            return None

        if isinstance(result, dict):
            if result.get("type") == "Image":
                self.current_image = result.get("data") 
            if result.get("type") == "Choice":
                self.step_index += 1 
                return result 

            self.step_index += 1
            return result

        self.step_index += 1
        return None

    def process_trigger(self, obj, player, scene):
        raw_params = getattr(obj, "trigger_params", getattr(obj, "params", ""))
        params = self.action_manager.parse_params(raw_params)
        
        if hasattr(obj, "condition") and obj.condition == Conditions.IF_FLAG:
            flag_a = params.get("flag_a") or params.get("flag")
            flag_b = params.get("flag_b")
            expected_val = params.get("value")
            operator = str(params.get("condition", "")).upper()

            if not flag_b:
                if not game_state.check_flag(flag_a, expected_val):
                    return None
                
            else:
                val_a = game_state.get_flag(flag_a)
                val_b = game_state.get_flag(flag_b)
                condition_met = False

                if operator == "AND":
                    condition_met = (val_a == expected_val) and (val_b == expected_val)
                elif operator == "OR":
                    condition_met = (val_a == expected_val) or (val_b == expected_val)
                elif operator == "EQUAL":
                    condition_met = (val_a == val_b)
                elif operator == "NOT_EQUAL":
                    condition_met = (val_a != val_b)

                if not condition_met:
                    return None

        should_kill = False
        if hasattr(obj, "condition") and obj.condition in [Conditions.ON_STAY, Conditions.IF_FLAG, Conditions.ON_ENTER] and not hasattr(obj, "interaction_type"):
             should_kill = params.get("kill", True)

        if hasattr(obj, "data") and obj.data.get("scripted_events"):
            sequence = obj.data.get("scripted_events")
            blocking = params.get("blocking", False)

            obj_id = getattr(obj, "id", None)
            self.start_sequence(sequence, blocking, source_id=obj_id)
            
            if should_kill:
                obj.kill()
            return None 

        act = getattr(obj, "trigger_action", getattr(obj, "action", "None"))
        if act and act != "None":
            obj_id = getattr(obj, "id", None)
            result = self.action_manager.execute(act, raw_params, player, scene, source_id=obj_id)
            
            if result:
                blocking_param = params.get("blocking", None)
                
                if blocking_param is not None:
                    result["blocking"] = blocking_param
                else:
                    result["blocking"] = self.is_blocking

            if act in [Actions.TELEPORT, Actions.CHANGE_LEVEL]: 
                should_kill = False
            
            if should_kill:
                obj.kill()
                if hasattr(obj, "id") and obj.id:
                    game_state.register_interaction(obj.id)

            return result
           
        return None