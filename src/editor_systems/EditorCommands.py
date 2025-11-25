from PySide6.QtCore import Qt
from src.Game_Constants import MAPS

class Command:
    """
    Abstract base class for the Command design pattern.
    Defines the interface that all reversible actions must implement to support Undo/Redo operations.
    """
    def execute(self):
        """
        Description: Performs the logic of the command.
        Functionality:
            - This method is called when the command is first pushed to the history or during a Redo operation.
            - It must apply the changes to the application state (Data Model and UI).
        """
        pass
    def undo(self): 
        """
        Description: Reverts the logic of the command.
        Functionality:
            - This method is called during an Undo operation.
            - It must restore the application state to exactly how it was before 'execute' was called.
        """
        pass

class UndoManager:
    """
    Manages the history of commands for the Undo/Redo system.
    It maintains two stacks to track past actions and reverted actions, allowing navigation through the editing history.
    """
    def __init__(self):
        """
        Description: Initializes the UndoManager with empty history stacks.
        """
        self.undo_stack = []
        self.redo_stack = []

    def push(self, command, execute_now=True):
        """
        Description: Registers a new command into the history.
        Parameters:
            command (Command): The command instance to be stored.
            execute_now (bool): If True, the command's execute method is called immediately. 
                                If False, it assumes the action was already performed (e.g., via drag-and-drop) 
                                and only stores the state for future reversal.
        Functionality:
            - Pushes the command onto the 'undo_stack'.
            - Clears the 'redo_stack', as a new action invalidates the previous future history.
            - Executes the command logic if 'execute_now' is set to True.
        """
        self.undo_stack.append(command)
        self.redo_stack.clear()
        if execute_now: command.execute()

    def undo(self):
        """
        Description: Reverts the most recent command.
        Functionality:
            - Pops the last command from the 'undo_stack'.
            - Calls the command's .undo() method.
            - Pushes the command onto the 'redo_stack'.
        """
        if not self.undo_stack: return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        """
        Description: Re-applies the most recently undone command.
        Functionality:
            - Pops the last command from the 'redo_stack'.
            - Calls the command's .execute() method.
            - Pushes the command back onto the 'undo_stack'.
        """
        if not self.redo_stack: return
        cmd = self.redo_stack.pop()
        cmd.execute()
        self.undo_stack.append(cmd)

class CmdAddObject(Command):
    """
    Concrete command to handle the creation of a new game object.
    """
    def __init__(self, editor, zone_key, obj_data):
        """
        Description: Initializes the add command.
        Parameters:
            editor (LevelEditor): Reference to the main editor controller to access data and UI methods.
            zone_key (str): The unique identifier of the zone where the object will be added (e.g., "(0, 0)").
            obj_data (dict): The data dictionary representing the new object.
        """
        self.editor = editor
        self.zone_key = zone_key
        self.obj_data = obj_data
    def execute(self):
        """
        Description: Adds the object to the data model and refreshes the view.
        Functionality:
            - Appends the object data to the specific zone list in 'current_data'.
            - Triggers a UI refresh to show the new object on the canvas and list.
            - Selects the newly created object.
        """
        if self.zone_key not in self.editor.current_data["zones"]:
            self.editor.current_data["zones"][self.zone_key] = []
        self.editor.current_data["zones"][self.zone_key].append(self.obj_data)
        self.editor.populate_views_for_current_zone()
        self.editor.select_object_by_id(self.obj_data["id"])
    def undo(self):
        """
        Description: Removes the added object, effectively undoing the creation.
        Functionality:
            - Removes the object reference from the zone list in 'current_data'.
            - Triggers a UI refresh to remove the object from the canvas and list.
        """
        zones = self.editor.current_data.get("zones", {})
        if self.zone_key in zones and self.obj_data in zones[self.zone_key]:
            zones[self.zone_key].remove(self.obj_data)
        self.editor.populate_views_for_current_zone()

class CmdDeleteObject(Command):
    """
    Concrete command to handle the deletion of a single game object.
    """
    def __init__(self, editor, zone_key, obj_data, index):
        """
        Description: Initializes the delete command.
        Parameters:
            editor (LevelEditor): Reference to the main editor controller.
            zone_key (str): The zone identifier containing the object.
            obj_data (dict): The data dictionary of the object to be deleted.
            index (int): The original index of the object in the list, required to restore it at the correct Z-order.
        """
        self.editor = editor
        self.zone_key = zone_key
        self.obj_data = obj_data
        self.index = index
    def execute(self):
        """
        Description: Removes the object from the data model.
        Functionality:
            - Removes the object dictionary from the zone list in 'current_data'.
            - Refreshes the view.
        """
        zones = self.editor.current_data.get("zones", {})
        if self.zone_key in zones:
            if self.obj_data in zones[self.zone_key]:
                zones[self.zone_key].remove(self.obj_data)
        self.editor.populate_views_for_current_zone()
    def undo(self):
        """
        Description: Restores the deleted object to its original position.
        Functionality:
            - Inserts the object data back into the zone list at the stored 'index'.
            - Refreshes the view and re-selects the restored object.
        """
        if self.zone_key not in self.editor.current_data["zones"]:
            self.editor.current_data["zones"][self.zone_key] = []
        self.editor.current_data["zones"][self.zone_key].insert(self.index, self.obj_data)
        self.editor.populate_views_for_current_zone()
        self.editor.select_object_by_id(self.obj_data["id"])

class CmdPropertyChange(Command):
    """
    Concrete command to handle modification of a single property of an object.
    Used for simple values like integers, floats, strings, booleans, or colors.
    """
    def __init__(self, editor, obj_data, key, old_val, new_val):
        """
        Description: Initializes the property change command.
        Parameters:
            editor (LevelEditor): Reference to the main editor controller.
            obj_data (dict): The dictionary of the object being modified.
            key (str): The specific key in the dictionary to update (e.g., 'x', 'image_path').
            old_val: The value before the change (for Undo).
            new_val: The value after the change (for Execute/Redo).
        """
        self.editor = editor
        self.obj_data = obj_data
        self.key = key
        self.old_val = old_val
        self.new_val = new_val
    def execute(self):
        """
        Description: Applies the new property value.
        Functionality:
            - Updates the key in the object's data dictionary.
            - Calls 'refresh_ui_for_object' to update the UI widgets and visual canvas item.
        """
        self.obj_data[self.key] = self.new_val
        self.editor.refresh_ui_for_object(self.obj_data)
    def undo(self):
        """
        Description: Reverts the property to its previous value.
        Functionality:
            - Restores the key in the object's data dictionary to 'old_val'.
            - Calls 'refresh_ui_for_object' to update the UI widgets and visual canvas item.
        """
        self.obj_data[self.key] = self.old_val
        self.editor.refresh_ui_for_object(self.obj_data)

class CmdTransform(Command):
    """
    Concrete command specialized for geometric transformations (Movement and Resizing).
    It groups changes to Position (X, Y) and Hitbox/Offset into a single atomic transaction.
    Typically used by Drag & Drop operations on the canvas.
    """
    def __init__(self, editor, obj_data, old_pos, new_pos, old_offset, new_offset):
        """
        Description: Initializes the transform command.
        Parameters:
            editor (LevelEditor): Reference to the main editor controller.
            obj_data (dict): The dictionary of the object being transformed.
            old_pos (tuple): (x, y) coordinates before the move.
            new_pos (tuple): (x, y) coordinates after the move.
            old_offset (list): [dx, dy, dw, dh] hitbox offset before the change.
            new_offset (list): [dx, dy, dw, dh] hitbox offset after the change.
        """
        self.editor = editor
        self.obj_data = obj_data
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.old_offset = old_offset
        self.new_offset = new_offset
    def execute(self):
        """
        Description: Applies the new position and offset.
        """
        self.obj_data['x'] = self.new_pos[0]
        self.obj_data['y'] = self.new_pos[1]
        self.obj_data['collision_rect_offset'] = self.new_offset
        self.editor.refresh_ui_for_object(self.obj_data)
    def undo(self):
        """
        Description: Restores the original position and offset.
        """
        self.obj_data['x'] = self.old_pos[0]
        self.obj_data['y'] = self.old_pos[1]
        self.obj_data['collision_rect_offset'] = self.old_offset
        self.editor.refresh_ui_for_object(self.obj_data)

class CmdBulkDelete(Command):
    """
    Concrete command for optimized bulk deletion of multiple objects.
    Prevents multiple UI refreshes and index errors when deleting groups of items.
    """
    def __init__(self, editor, zone_key, items_list):
        """
        Description: Initializes the bulk delete command.
        Parameters:
            editor (LevelEditor): Reference to the main editor controller.
            zone_key (str): The zone identifier.
            items_list (list): A list of tuples, where each tuple contains (index, obj_data).
        Functionality:
            - Sorts the items_list by index in descending order. This is crucial for Undo operations
              to ensure items are re-inserted correctly without shifting subsequent indices.
        """
        self.editor = editor
        self.zone_key = zone_key
        self.items_list = sorted(items_list, key=lambda x: x[0], reverse=True)

    def execute(self):
        """
        Description: Removes all specified objects in a single transaction.
        Functionality:
            - Iterates through the list and removes each object from the data model.
            - Performs a single UI refresh after all deletions are complete.
        """
        zones = self.editor.current_data.get("zones", {})
        if self.zone_key in zones:
            target_list = zones[self.zone_key]

            for _, obj_data in self.items_list:
                if obj_data in target_list:
                    target_list.remove(obj_data)

        self.editor.populate_views_for_current_zone()

    def undo(self):
        """
        Description: Restores all deleted objects.
        Functionality:
            - Iterates through the list in reverse order (original index ascending effectively, due to initial sort).
            - Re-inserts each object into the data list at its original index.
            - Performs a single UI refresh.
        """
        if self.zone_key not in self.editor.current_data["zones"]:
            self.editor.current_data["zones"][self.zone_key] = []
            
        target_list = self.editor.current_data["zones"][self.zone_key]
        
        for index, obj_data in reversed(self.items_list):
            target_list.insert(index, obj_data)
            
        self.editor.populate_views_for_current_zone()

class CmdResize(Command):
    """
    Specific command to change size in Primitives.
    Saves the new width and height.
    """
    def __init__(self, editor, obj_data, old_size, new_size):
        self.editor = editor
        self.obj_data = obj_data
        self.old_w, self.old_h = old_size
        self.new_w, self.new_h = new_size

    def execute(self):
        self.obj_data['width'] = self.new_w
        self.obj_data['height'] = self.new_h
        self.editor.refresh_ui_for_object(self.obj_data)

    def undo(self):
        self.obj_data['width'] = self.old_w
        self.obj_data['height'] = self.old_h
        self.editor.refresh_ui_for_object(self.obj_data)