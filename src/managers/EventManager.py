from src.core.GameState import game_state
from src.utils.Game_Enums import Conditions, Actions
from src.managers.ScriptManager import script_manager
from src.scripting.Interpreter import Interpreter
from src.core.GameResults import WaitResult
import inspect

class EventManager:
    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.current_script_generator = None
        self.waiting_for_action = False
        
        self.is_active = False
        self.is_blocking = False
        
        self.current_sequence = []
        self.step_index = 0
        
        self.wait_timer = 0
        self.current_image = None

        self.current_source_id = None

    def start_script(self, generator):
        print(generator)
        if inspect.isgenerator(generator):
            self.current_script_generator = generator
            self.waiting_for_action = False
            
            return self.step_script() 
        else:
            return generator
        
    def step_script(self):
        if not self.current_script_generator: return None

        try:
            result = next(self.current_script_generator)
            if isinstance(result, WaitResult):
                self.wait_timer = result.duration
                if result.blocking:
                    self.is_blocking = True
                return result

            if result and hasattr(result, "blocking") and result.blocking:
                self.waiting_for_action = True
                return result
            
            return result

        except StopIteration:
            print("[EventManager] Script .fer finished.")
            self.current_script_generator = None
            self.waiting_for_action = False
            return None
        except Exception as e:
            print(f"[EventManager] CRITIC error in corroutine: {e}")
            self.current_script_generator = None
            return None

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
        if self.current_script_generator:
            if self.wait_timer > 0:
                self.wait_timer -= delta_time
                
                if self.wait_timer <= 0:
                    self.wait_timer = 0
                    self.is_blocking = False
                else:
                    return None

            if not self.waiting_for_action:
                return self.step_script()
            
            return None

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

        if result is not None:
            self.step_index += 1
            return result

        self.step_index += 1
        return None

    def process_trigger(self, obj, player, scene):
        if hasattr(obj, "script") and obj.script:
            if self.current_script_generator:
                return None
            script_name = obj.script
            func_name = getattr(obj, "function", "main") or "main"
            ast = script_manager.get_script(script_name)
            
            if ast:
                obj_id = getattr(obj, "id", "UNKNOWN_SOURCE")

                interpreter = Interpreter(self.action_manager, player, scene, source_id=obj_id)
                interpreter.load(ast)
                print(f"[EventManager] Init Script: {script_name} -> {func_name}()")
                
                try:
                    gen_or_val = interpreter.run_function(func_name)
                    return self.start_script(gen_or_val)

                except Exception as e:
                    print(f"[EventManager] Error executing script '{script_name}': {e}")
                    return None
            else:
                print(f"[EventManager] Error: script '{script_name}' not found")
                return None

        # OLD SYSTEM

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
                if self.is_blocking and hasattr(result, "blocking"):
                    pass

            if act in [Actions.TELEPORT, Actions.CHANGE_LEVEL]: 
                should_kill = False
            
            if should_kill:
                obj.kill()
                if hasattr(obj, "id") and obj.id:
                    game_state.register_interaction(obj.id)

            return result
           
        return None
    
    def notify_action_completed(self):
        if self.current_script_generator and self.waiting_for_action:
            self.waiting_for_action = False