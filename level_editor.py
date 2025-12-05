import sys
import json
import os
import time
import copy
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QListWidget, QInputDialog, QMessageBox, QAbstractItemView
)
from PySide6.QtGui import QPixmap, QBrush, QColor, QPen, QKeySequence, QShortcut, QPainter
from PySide6.QtCore import Qt, QRectF, QPointF
from ui_editor import Ui_LevelEditor
from src.editor_systems.EditorCommands import *
from src.editor_systems.EditorGraphics import *
from src.Game_Constants import MAPS, SCREEN_WIDTH, SCREEN_HEIGHT
from src.Game_Enums import Actions, Conditions, ObjectTypes

GAME_WIDTH = SCREEN_WIDTH
GAME_HEIGHT = SCREEN_HEIGHT
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
AUDIO_EXTENSIONS = ('.wav', '.mp3', '.ogg')

class LevelEditor(QMainWindow, Ui_LevelEditor):
    """
    Main controller for the LevelEditor
    Manages the GUI, handles user input, renders the visual representation of the level,
    and orchestrates the synchronization between the raw JSON data and the visual elements.
    It acts as the "Director" in the MVC pattern, connecting the Data (JSON) with the View (Qt Widgets / Canvas)
    """
    def __init__(self):
        """
        :Description: Initializes the main editor window and subsystems.

        Functionality:
            - Sets up the UI from Ui_LevelEditor.
            - Initializes the UndoManager for history tracking.
            - Configures the QGraphicsScene (the visual canvas).
            - Connects all Qt signals (buttons, spinboxes, combos) to their respective slot methods.
            - Sets up keyboard shortcuts for navigation and editing.
            - Populates initial data for combo boxes (images, sounds, maps).
        """
        super().__init__()
        self.setupUi(self)
        self.undo_manager = UndoManager()
        self.is_programmatic_change = False 
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.current_data = {"zones": {}}
        self.image_paths = []
        self.clipboard_data = None
        self.current_scene = QGraphicsScene()
        self.canvas_view.setScene(self.current_scene)
        self.current_scene.setSceneRect(0, 0, GAME_WIDTH, GAME_HEIGHT)
        self.current_scene.setBackgroundBrush(QBrush(QColor(50, 50, 50)))
        self.draw_game_border()
        self.current_scene.selectionChanged.connect(self.on_scene_selection_changed)
        self.current_hitbox_item = None
        self._updating_selection_from_canvas = False 
        self.all_image_combos = [self.prop_image_path_combo, self.prop_flash_image_path_combo, self.prop_used_image_path_combo]

        self.action_new_map.triggered.connect(self.create_new_json_from_map)
        self.action_load_json.triggered.connect(self.load_json)
        self.action_save_json.triggered.connect(self.save_json)
        self.btn_add_object.clicked.connect(self.add_new_object)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)
        self.combo_zone_selector.currentIndexChanged.connect(self.populate_views_for_current_zone)

        self.list_objects.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_objects.currentItemChanged.connect(self.on_object_selected)

        self.prop_x.valueChanged.connect(lambda v: self.on_property_changed('x', v))
        self.prop_y.valueChanged.connect(lambda v: self.on_property_changed('y', v))
        self.prop_z_index.valueChanged.connect(lambda v: self.on_property_changed('z_index', v))
        self.prop_reflection_offset.valueChanged.connect(lambda v: self.on_property_changed('reflection_offset_y', v))
        self.prop_resize_factor.valueChanged.connect(lambda v: self.on_property_changed('resize_factor', v))
        self.prop_width.valueChanged.connect(lambda v: self.on_property_changed('width', v))
        self.prop_height.valueChanged.connect(lambda v: self.on_property_changed('height', v))
        self.prop_color_r.valueChanged.connect(lambda: self.on_property_changed('color', None))
        self.prop_color_g.valueChanged.connect(lambda: self.on_property_changed('color', None))
        self.prop_color_b.valueChanged.connect(lambda: self.on_property_changed('color', None))
        self.prop_border_width.valueChanged.connect(lambda v: self.on_property_changed('border_width', v))
        self.prop_hitbox_dx.valueChanged.connect(self.on_hitbox_changed)
        self.prop_hitbox_dy.valueChanged.connect(self.on_hitbox_changed)
        self.prop_hitbox_dw.valueChanged.connect(self.on_hitbox_changed)
        self.prop_hitbox_dh.valueChanged.connect(self.on_hitbox_changed)
        self.prop_anim_speed.valueChanged.connect(lambda v: self.on_property_changed('animation_speed', v))
        self.prop_type.currentTextChanged.connect(lambda v: self.on_property_changed('type', v))
        self.prop_image_path_combo.currentTextChanged.connect(lambda v: self.on_property_changed('image_path', v))
        self.prop_flash_image_path_combo.currentTextChanged.connect(lambda v: self.on_property_changed('flash_image_path', v))
        self.prop_charge_sound_combo.currentTextChanged.connect(lambda v: self.on_property_changed('charge_sound_path', v))
        self.prop_used_image_path_combo.currentTextChanged.connect(lambda v: self.on_property_changed('used_image_path', v))
        self.prop_interaction_duration.valueChanged.connect(lambda v: self.on_property_changed('interaction_duration', v))
        self.prop_is_passable.stateChanged.connect(lambda v: self.on_property_changed('is_passable', bool(v)))
        self.prop_starts_hidden.stateChanged.connect(lambda v: self.on_property_changed('starts_hidden', bool(v)))
        self.prop_is_ground.stateChanged.connect(lambda v: self.on_property_changed('is_ground', bool(v)))

        self.prop_trigger_condition.currentTextChanged.connect(lambda v: self.on_property_changed('trigger_condition', v))
        self.prop_trigger_action.currentTextChanged.connect(lambda v: self.on_property_changed('trigger_action', v))
        self.prop_trigger_params.textChanged.connect(self.on_trigger_params_changed)
        self.btn_seq_add.clicked.connect(self.add_sequence_step)
        self.btn_seq_remove.clicked.connect(self.remove_sequence_step)
        self.btn_seq_up.clicked.connect(lambda: self.move_sequence_step(-1))
        self.btn_seq_down.clicked.connect(lambda: self.move_sequence_step(1))
        self.list_trigger_sequence.currentRowChanged.connect(lambda row: self.load_selected_step_to_ui())
        self.prop_step_action.currentTextChanged.connect(self.update_selected_step_data)
        self.prop_step_params.textChanged.connect(self.update_selected_step_data)


        self.btn_anim_add.clicked.connect(self.add_animation_frame)
        self.btn_anim_remove.clicked.connect(self.remove_animation_frame)
        self.prop_image_path_combo.currentTextChanged.connect(self.update_image_preview)
        self.prop_type.currentTextChanged.connect(self.on_main_type_changed)
        self.btn_browse_image.clicked.connect(lambda: self.browse_file_for_combo(self.prop_image_path_combo))
        self.btn_browse_flash.clicked.connect(lambda: self.browse_file_for_combo(self.prop_flash_image_path_combo))
        self.btn_browse_charge.clicked.connect(lambda: self.browse_audio_for_combo(self.prop_charge_sound_combo))
        self.btn_browse_used.clicked.connect(lambda: self.browse_file_for_combo(self.prop_used_image_path_combo))
        self.shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut_up.activated.connect(lambda: self.navigate_zone(0, -1))
        self.shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut_down.activated.connect(lambda: self.navigate_zone(0, 1))
        self.shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut_left.activated.connect(lambda: self.navigate_zone(-1, 0))
        self.shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut_right.activated.connect(lambda: self.navigate_zone(1, 0))
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_json)
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(self.copy_object)
        self.shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)
        self.shortcut_paste.activated.connect(self.paste_object)
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_undo.activated.connect(self.perform_undo)
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.shortcut_redo.activated.connect(self.perform_redo)
        self.shortcut_delete = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.shortcut_delete.activated.connect(self.delete_selected_object)
        self.combo_map_select.addItems(list(MAPS.keys()))
        self.chk_layer_obstacles.stateChanged.connect(self.update_layers)
        self.chk_layer_triggers.stateChanged.connect(self.update_layers)
        self.chk_layer_interactables.stateChanged.connect(self.update_layers)
        self.chk_lock_ground.stateChanged.connect(self.update_layers)
        self.populate_image_combos()
        self.populate_sound_combos()
        self.disable_property_panel()

    def perform_undo(self): self.undo_manager.undo()
    def perform_redo(self): self.undo_manager.redo()
    def select_object_by_id(self, obj_id):
        for i in range(self.list_objects.count()):
            item = self.list_objects.item(i)
            if item.data(Qt.UserRole).get("id") == obj_id:
                self.list_objects.setCurrentItem(item)
                break

    def refresh_ui_for_object(self, obj_data):
        """
        Description: Populates the property panel (left sidebar) with the data of the selected object.
        Parameters:
            obj_data (dict): The data dictionary of the object to display.
        Functionality:
            - Sets a flag 'is_programmatic_change' to True to prevent triggering 'on_property_changed' loops.
            - Updates every widget (SpinBox, ComboBox, CheckBox) with values from obj_data.
            - Handles logic for specific types (e.g., showing specific stacks for 'Interactable' vs 'Trigger').
            - Updates the list item text and the canvas visual representation to ensure sync.
            - Resets 'is_programmatic_change' to False.
        """
        current = self.list_objects.currentItem()
        if current and current.data(Qt.UserRole) is obj_data:
            self.is_programmatic_change = True
            
            self.prop_x.setValue(obj_data.get('x', 0))
            self.prop_y.setValue(obj_data.get('y', 0))
            self.prop_z_index.setValue(int(obj_data.get('z_index', 0)))
            self.prop_reflection_offset.setValue(int(obj_data.get('reflection_offset_y', 0)))

            self.prop_width.setValue(int(obj_data.get('width', 50)))
            self.prop_height.setValue(int(obj_data.get('height', 50)))
            self.prop_border_width.setValue(int(obj_data.get('border_width', 0)))
            
            color = obj_data.get('color', [255, 255, 255])
            if isinstance(color, list) and len(color) >= 3:
                self.prop_color_r.setValue(color[0])
                self.prop_color_g.setValue(color[1])
                self.prop_color_b.setValue(color[2])
            
            self.prop_image_path_combo.setCurrentText(obj_data.get('image_path', 'None'))
            self.prop_resize_factor.setValue(float(obj_data.get('resize_factor', 4.0)))
            
            self.prop_is_passable.setChecked(obj_data.get('is_passable', False))
            self.prop_starts_hidden.setChecked(obj_data.get('starts_hidden', False))
            self.prop_is_ground.setChecked(obj_data.get('is_ground', False))

            hb = obj_data.get('collision_rect_offset', [0,0,0,0])
            self.prop_hitbox_dx.setValue(hb[0])
            self.prop_hitbox_dy.setValue(hb[1])
            self.prop_hitbox_dw.setValue(hb[2])
            self.prop_hitbox_dh.setValue(hb[3])

            self.prop_anim_list.clear()
            self.prop_anim_list.addItems(obj_data.get('animation_images', []))
            self.prop_anim_speed.setValue(float(obj_data.get('animation_speed', 0.1)))

            self.prop_flash_image_path_combo.setCurrentText(obj_data.get('flash_image_path', 'None'))
            self.prop_charge_sound_combo.setCurrentText(obj_data.get('charge_sound_path', 'None'))
            self.prop_used_image_path_combo.setCurrentText(obj_data.get('used_image_path', 'None'))
            self.prop_interaction_duration.setValue(int(obj_data.get('interaction_duration', 60)))

            self.prop_trigger_action.setCurrentText(obj_data.get("trigger_action", Actions.SET_FLAG))
            self.prop_trigger_params.setText(obj_data.get("trigger_params", ""))
            
            self.list_trigger_sequence.clear()
            sequence = obj_data.get("scripted_events", [])
            
            for step in sequence:
                action = step.get("action", Actions.WAIT)
                params = step.get("params", "")
                item_text = f"{action} ({params})"
                
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, step)
                self.list_trigger_sequence.addItem(list_item)
                
            self.group_step_detail.setEnabled(False)
            
            if self.list_trigger_sequence.count() > 0:
                self.list_trigger_sequence.setCurrentRow(0)
            
            current.setText(f"[{obj_data.get('type')}] {obj_data.get('id')}")
            pixmap_item = current.data(Qt.UserRole + 1)
            if pixmap_item: self.update_canvas_item(obj_data, pixmap_item)
            
            self.is_programmatic_change = False

    def browse_file_for_combo(self, combo_widget):
        start_dir = os.path.join(self.base_path, "assets")
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", start_dir, "Images (*.png *.jpg *.jpeg)")
        if filepath:
            try:
                rel_path = os.path.relpath(filepath, self.base_path).replace("\\", "/")
                if rel_path not in [combo_widget.itemText(i) for i in range(combo_widget.count())]:
                    combo_widget.addItem(rel_path)
                combo_widget.setCurrentText(rel_path)
            except ValueError: pass

    def copy_object(self):
        real_data = self.get_real_object_data()
        if not real_data:
            return
            
        self.clipboard_data = copy.deepcopy(real_data)
        print(f"Copiado: {self.clipboard_data.get('id')}")

    def paste_object(self):
        if not self.clipboard_data: return
        current_zone = self.combo_zone_selector.currentText()
        if not current_zone: return
        new_obj_data = copy.deepcopy(self.clipboard_data)
        new_id = f"obj_{int(time.time())}_{len(self.current_data['zones'][current_zone])}"
        new_obj_data['id'] = new_id
        new_obj_data['x'] += 20
        new_obj_data['y'] += 20
        cmd = CmdAddObject(self, current_zone, new_obj_data)
        self.undo_manager.push(cmd, execute_now=True)

    def add_new_object(self):
        """
        ## Description: 
            Creates a new object entity in the current zone.
        ## Functionality:
            - Generates a unique ID using timestamp and random entropy to prevent collisions.
            - Creates a default dictionary structure for a 'Primitive' type object.
            - Pushes a CmdAddObject command to the UndoManager (allowing Ctrl+Z to remove it).
            - Updates the view to show the new object immediately.
        """
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key: return
        new_id = f"obj_{int(time.time()*1000)}_{random.randint(0, 999)}"
        new_obj_data = {
            "id": new_id,
            
            "type": ObjectTypes.PRIMITIVE, 
            
            "x": GAME_WIDTH // 2, 
            "y": GAME_HEIGHT // 2,
            "image_path": "None",
            "resize_factor": 1,
            "is_passable": False,
            "starts_hidden": False,
            "collision_rect_offset": [0, 0, 0, 0],
            

            "width": 100,
            "height": 100,
            "color": [255, 255, 255],
            "border_width": 0, 
            
            "animation_images": [],
            "animation_speed": 0.1,
            "flash_image_path": "None",
            "charge_sound_path": "None",
            "used_image_path": "None", 
            "interaction_duration": 60, 
            "trigger_condition": Conditions.ON_STAY,    
            "trigger_action": Actions.SET_FLAG, 
            "trigger_params": ""
        }
        cmd = CmdAddObject(self, current_zone_key, new_obj_data)
        self.undo_manager.push(cmd, execute_now=True)

    def delete_selected_object(self):
        """
        ## Description: 
            Removes currently selected objects from the level.
        ## Functionality:
            - Identifies all selected items in the list.
            - Retrieves their real data references using IDs.
            - Wraps the deletion of multiple items into a single CmdBulkDelete command (atomic undo).
            - Executes the command to remove data and refresh the view.
        """
        selected_items = self.list_objects.selectedItems()
        if not selected_items:
            return

        current_zone_key = self.combo_zone_selector.currentText()
        zone_objects_list = self.current_data.get("zones", {}).get(current_zone_key, [])
        
        items_to_process = []
        
        for item in selected_items:
            row = self.list_objects.row(item)
            item_data = item.data(Qt.UserRole)
            obj_id = item_data.get("id")
            
            real_obj_data = next((obj for obj in zone_objects_list if obj.get("id") == obj_id), None)
            
            if real_obj_data:
                items_to_process.append((row, real_obj_data))
            else:
                print(f"Object {obj_id} visual but not in data.")
        
        if items_to_process:
            cmd = CmdBulkDelete(self, current_zone_key, items_to_process)
            self.undo_manager.push(cmd, execute_now=True)
            
            self.statusbar.showMessage(f"{len(items_to_process)} objects were deleted.", 3000)
            
            self.disable_property_panel()
            if self.current_hitbox_item:
                self.current_scene.removeItem(self.current_hitbox_item)
                self.current_hitbox_item = None

    def get_real_object_data(self):
        """
        ## Description: 
            Retrieves the actual reference to the object's data dictionary
        ## Returns: 
            - dict: The mutable dictionary representing the object in self.current_data
            - None: If no object is selected or found.
        ## Functionality:
            - Crucial for the Data-Driven architecture. Instead of relying on potentially stale data 
            - stored in the QListWidgetItem, this method uses the object's unique ID to linear search 
            - the 'self.current_data' source of truth. This ensures all edits (Undo/Redo, Properties) 
            - modify the persistent state directly.
        """
        current_item = self.list_objects.currentItem()
        if not current_item: return None
        
        item_data = current_item.data(Qt.UserRole)
        if not item_data: return None
        obj_id = item_data.get("id")
        
        zone = self.combo_zone_selector.currentText()
        if zone not in self.current_data["zones"]: return None

        for obj in self.current_data["zones"][zone]:
            if obj.get("id") == obj_id:
                return obj 
        return None

    # --- PROPERTY CHANGED ---
    
    def on_property_changed(self, key, new_value):
        """
        ## Description: 
            Slot called when a property widget value is modified by the user.
        ## Parameters:
            - key (str): The key in the data dictionary to update (e.g., 'x', 'image_path').
            - new_value (any): The new value to assign.
        ## Functionality:
            - Checks 'is_programmatic_change' to ignore internal updates.
            - Compares old vs new value to avoid unnecessary commands.
            - Pushes a CmdPropertyChange to UndoManager (execute_now=False because the UI already changed).
            - Updates the 'obj_data' dictionary directly.
            - Triggers a visual update on the canvas if necessary (e.g. changing color or position).
        """
        if self.is_programmatic_change: return
        obj_data = self.get_real_object_data()
        if not obj_data: return
        
        current_item = self.list_objects.currentItem()
        
        if key == "color":
            r = self.prop_color_r.value()
            g = self.prop_color_g.value()
            b = self.prop_color_b.value()
            final_value = [r, g, b]
        else:
            final_value = new_value

        old_value = obj_data.get(key)
        if old_value == final_value: return

        cmd = CmdPropertyChange(self, obj_data, key, old_value, final_value)
        self.undo_manager.push(cmd, execute_now=False)
        
        obj_data[key] = final_value
        
        if key == 'type' or key == 'id':
            current_item.setText(f"[{obj_data.get('type')}] {obj_data.get('id')}")
        
        current_item.setData(Qt.UserRole, obj_data)
        
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if pixmap_item:
            self.update_canvas_item(obj_data, pixmap_item)

    def on_hitbox_changed(self):
        if self.is_programmatic_change: return
        
        obj_data = self.get_real_object_data()
        if not obj_data: return

        old_offset = copy.deepcopy(obj_data.get('collision_rect_offset', [0,0,0,0]))
        new_offset = [
            self.prop_hitbox_dx.value(), self.prop_hitbox_dy.value(),
            self.prop_hitbox_dw.value(), self.prop_hitbox_dh.value()
        ]
        
        if old_offset == new_offset: return
        
        cmd = CmdPropertyChange(self, obj_data, 'collision_rect_offset', old_offset, new_offset)
        self.undo_manager.push(cmd, execute_now=False)
        
        obj_data['collision_rect_offset'] = new_offset
        
        current_item = self.list_objects.currentItem()
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if pixmap_item: self.update_canvas_item(obj_data, pixmap_item)

    def on_trigger_params_changed(self):
        if self.is_programmatic_change: return
        
        obj_data = self.get_real_object_data()
        if not obj_data: return
        
        obj_data['trigger_params'] = self.prop_trigger_params.toPlainText()

    def navigate_zone(self, dx, dy):
        focus_widget = QApplication.focusWidget()
        if isinstance(focus_widget, (QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox)): return
        
        current_text = self.combo_zone_selector.currentText()
        if not current_text: return

        try:
            content = current_text.replace("(", "").replace(")", "")
            parts = content.split(",")
            cy, cx = int(parts[0]), int(parts[1])
        except: return

        ny, nx = cy + dy, cx + dx

        current_map_name = self.combo_map_select.currentText() 
        current_map_matrix = MAPS.get(current_map_name, [])
        
        if ny < 0 or ny >= len(current_map_matrix) or nx < 0 or nx >= len(current_map_matrix[0]): 
            print(f"Map limit reached {current_map_name}")
            return
            
        if current_map_matrix[ny][nx] == 0: 
            print(f"Invalid zone (0) in map: {current_map_name}")
            return

        target = f"({ny}, {nx})"
        idx = self.combo_zone_selector.findText(target)
        if idx != -1: 
            self.combo_zone_selector.setCurrentIndex(idx)
        else:
            self.current_data["zones"][target] = []
            self.combo_zone_selector.addItem(target)
            self.combo_zone_selector.setCurrentText(target)

    def on_scene_selection_changed(self):
        """
        ## Description: 
            Synchronizes selection from the Canvas to the List.
        ## Functionality:
            - Triggered when user clicks items in the visual scene.
            - Sets a flag '_updating_selection_from_canvas' to prevent feedback loops.
            - Finds the corresponding items in the QListWidget and selects them.
            - Updates the property panel to show the data of the primary selected item.
        """
        if self.list_objects.signalsBlocked(): return
        
        self._updating_selection_from_canvas = True 
        
        try:
            selected_graphics_items = self.current_scene.selectedItems()
            
            if not selected_graphics_items:
                self.list_objects.blockSignals(True)
                self.list_objects.clearSelection()
                self.list_objects.blockSignals(False)
                self.disable_property_panel()
                return

            selected_ids = []
            for item in selected_graphics_items:
                if isinstance(item, LevelObjectItem):
                    obj_id = item.obj_data.get("id")
                    if obj_id: selected_ids.append(obj_id)
                elif hasattr(item, "parent_item") and isinstance(item.parent_item, LevelObjectItem):
                     obj_id = item.parent_item.obj_data.get("id")
                     if obj_id: selected_ids.append(obj_id)

            self.list_objects.blockSignals(True)
            self.list_objects.clearSelection()
            
            first_match_item = None
            
            for i in range(self.list_objects.count()):
                list_item = self.list_objects.item(i)
                data = list_item.data(Qt.UserRole)
                
                if data.get("id") in selected_ids:
                    list_item.setSelected(True)
                    if not first_match_item: first_match_item = list_item
            
            self.list_objects.blockSignals(False)

            if len(selected_ids) == 1 and first_match_item:
                self.list_objects.setCurrentItem(first_match_item)
                self.on_object_selected(first_match_item, None)
                
            elif len(selected_ids) > 1:
                self.disable_property_panel()
                
        finally:
            self._updating_selection_from_canvas = False

    def sync_obj_pos_ui(self, x, y):
        self.is_programmatic_change = True
        self.prop_x.setValue(x)
        self.prop_y.setValue(y)
        self.is_programmatic_change = False
        self.update_hitbox_position_only()

    def sync_hitbox_pos_ui(self, dx, dy):
        self.is_programmatic_change = True
        self.prop_hitbox_dx.setValue(dx)
        self.prop_hitbox_dy.setValue(dy)
        self.is_programmatic_change = False

    def sync_hitbox_size_ui(self, dw, dh):
        self.is_programmatic_change = True
        self.prop_hitbox_dw.setValue(dw)
        self.prop_hitbox_dh.setValue(dh)
        self.is_programmatic_change = False

    def update_hitbox_position_only(self):
        if not self.current_hitbox_item or not self.list_objects.currentItem(): 
            return
            
        real_data = self.get_real_object_data()
        if not real_data:
            return

        self.current_hitbox_item.ignore_movement = True
        
        pixmap_item = self.list_objects.currentItem().data(Qt.UserRole + 1)
        
        if pixmap_item:
            offset = real_data.get("collision_rect_offset", [0, 0, 0, 0])
            
            sprite_pos = pixmap_item.pos()

            self.current_hitbox_item.setPos(sprite_pos.x() + offset[0], sprite_pos.y() + offset[1])
            
        self.current_hitbox_item.ignore_movement = False

    def _block_all_property_signals(self, block: bool): pass 

    def disable_property_panel(self):
        self.properties_box.setEnabled(False)
        self.group_animation.setEnabled(False)
        self.group_interaction.setEnabled(False)
        if self.current_hitbox_item:
            self.current_scene.removeItem(self.current_hitbox_item)
            self.current_hitbox_item = None

    def enable_property_panel(self):
        self.properties_box.setEnabled(True)
        self.on_main_type_changed()

    def on_main_type_changed(self):
        current_type = self.prop_type.currentText()
        is_primitive = (current_type == ObjectTypes.PRIMITIVE)

        self.label_2.setVisible(not is_primitive)
        self.prop_image_path_combo.setVisible(not is_primitive)
        self.btn_browse_image.setVisible(not is_primitive)
        self.label_12.setVisible(not is_primitive)
        self.prop_image_preview.setVisible(not is_primitive)
        self.label_8.setVisible(not is_primitive)
        self.prop_resize_factor.setVisible(not is_primitive)
        self.lbl_border.setVisible(is_primitive)
        self.prop_border_width.setVisible(is_primitive)
        
        self.lbl_size.setVisible(is_primitive)
        self.prop_width.setVisible(is_primitive)
        self.prop_height.setVisible(is_primitive)
        
        self.lbl_color.setVisible(is_primitive)
        self.prop_color_r.setVisible(is_primitive)
        self.prop_color_g.setVisible(is_primitive)
        self.prop_color_b.setVisible(is_primitive)

        self.group_interaction.setEnabled(current_type in [ObjectTypes.INTERACTABLE, ObjectTypes.TRIGGER])
        self.group_animation.setEnabled(True)
        if current_type == ObjectTypes.INTERACTABLE: self.prop_main_stack.setCurrentIndex(0)
        elif current_type == ObjectTypes.TRIGGER: self.prop_main_stack.setCurrentIndex(1)
        else: self.prop_main_stack.setCurrentIndex(0)

    def create_new_json_from_map(self):
        """
        ## Description: 
            Generates a scaffold JSON file based on a game map matrix.
        ## Functionality:
            - Prompts the user to select a Map layout (defined in Game_Constants).
            - Iterates through the 2D matrix of the selected map.
            - For every '1' found in the matrix, creates an empty zone entry in the JSON (e.g., "(0, 0)").
            - Saves the file and immediately loads it into the editor.
        """
        if not MAPS:
            QMessageBox.warning(self, "Error", "No maps in Game_Constants.py (MAPS)")
            return

        map_names = list(MAPS.keys())
        name, ok = QInputDialog.getItem(self, "Nuevo Nivel", "Selecciona el Mapa Base:", map_names, 0, False)
        
        if not ok or not name:
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Crear Nuevo Archivo JSON", self.base_path, "JSON (*.json)")
        if not filename:
            return
        
        matrix = MAPS[name]
        new_data = {"zones": {}}
        count = 0
        
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                if matrix[y][x] == 1:
                    zone_key = f"({y}, {x})"
                    new_data["zones"][zone_key] = []
                    count += 1
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=4)
            
            QMessageBox.information(self, "Éxito", f"Se creó '{os.path.basename(filename)}' con {count} zonas.")
            
            self.load_json_from_path(filename) 
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el archivo:\n{e}")

    def load_json_from_path(self, filepath):
        """
        Loads a specific JSON file without the selection dialogue
        """
        if not filepath: return
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            self.current_data = {"zones": {}}

        self.undo_manager = UndoManager()
        
        self.combo_zone_selector.blockSignals(True)
        self.combo_zone_selector.clear()
        self.combo_zone_selector.addItems(list(self.current_data.get("zones", {}).keys()))
        self.combo_zone_selector.blockSignals(False)
        
        self.populate_views_for_current_zone()

    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Cargar JSON", self.base_path, "JSON (*.json)")
        if not filepath: return
        try:
            with open(filepath, "r", encoding="utf-8") as f: self.current_data = json.load(f)
        except: self.current_data = {"zones": {}}
        self.undo_manager = UndoManager()
        self.combo_zone_selector.blockSignals(True)
        self.combo_zone_selector.clear()
        self.combo_zone_selector.addItems(list(self.current_data.get("zones", {}).keys()))
        self.combo_zone_selector.blockSignals(False)
        self.populate_views_for_current_zone()

    def sanitize_before_save(self):
        zones = self.current_data.get("zones", {})
        for zone_key, objects in zones.items():
            for obj in objects:
                if obj.get("image_path") == "None": obj["image_path"] = ""
                if obj.get("flash_image_path") == "None": obj["flash_image_path"] = ""
                if obj.get("charge_sound_path") == "None": obj["charge_sound_path"] = ""
                if obj.get("used_image_path") == "None": obj["used_image_path"] = ""
                try: obj["interaction_duration"] = int(obj.get("interaction_duration", 60))
                except: obj["interaction_duration"] = 60
                try: obj["resize_factor"] = float(obj.get("resize_factor", 1))
                except: obj["resize_factor"] = 1.0
                try: obj["z_index"] = int(obj.get("z_index", 0))
                except: obj["z_index"] = 0
                try: obj["border_width"] = int(obj.get("border_width", 0))
                except: obj["border_width"] = 0
                try: obj["reflection_offset_y"] = int(obj.get("reflection_offset_y", 0))
                except: obj["reflection_offset_y"] = 0
                itype = obj.get("interaction_type", "None")
                if itype == "Note":
                    d = obj.get("interaction_data")
                    if isinstance(d, list): obj["interaction_data"] = "\n".join(d)
                    elif d is None: obj["interaction_data"] = ""
                    else: obj["interaction_data"] = str(d)
                elif itype == "Image":
                    d = obj.get("interaction_data")
                    obj["interaction_data"] = "" if d in (None, "None") else str(d)
                elif itype == "Door":
                    if obj.get("interaction_data") is None: obj["interaction_data"] = {}
                else: obj["interaction_data"] = ""

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", self.base_path, "JSON (*.json)")
        if not filepath: return
        try: self.sanitize_before_save()
        except: pass
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.current_data, f, indent=4, ensure_ascii=False)
            print("Guardado exitoso.")
        except Exception as e: print(f"Error: {e}")

    def populate_image_combos(self):
        self.image_paths = ["None"]
        for folder in ["assets/images", "assets/animations"]:
            full = os.path.join(self.base_path, folder)
            if not os.path.exists(full): continue
            for root, _, files in os.walk(full):
                for f in files:
                    if f.lower().endswith(IMAGE_EXTENSIONS):
                        rel = os.path.relpath(os.path.join(root, f), self.base_path).replace("\\", "/")
                        self.image_paths.append(rel)
        for combo in self.all_image_combos:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(self.image_paths)
            combo.blockSignals(False)

    def populate_views_for_current_zone(self):
        self.list_objects.clear()
        self.current_scene.clear()
        self.draw_game_border()
        self.current_hitbox_item = None
        self.disable_property_panel()
        zone = self.combo_zone_selector.currentText()
        if not zone or "zones" not in self.current_data: return
        if zone not in self.current_data["zones"]: self.current_data["zones"][zone] = []
        for obj in self.current_data["zones"].get(zone, []):
            item_text = f"[{obj.get('type','Obj')}] {obj.get('id','NO_ID')} "
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, obj)
            self.list_objects.addItem(item)
            pix_item = self.draw_object_on_canvas(obj)
            if pix_item: item.setData(Qt.UserRole + 1, pix_item)
        self.update_layers()

    def draw_game_border(self):
        border = QGraphicsRectItem(0, 0, GAME_WIDTH, GAME_HEIGHT)
        
        pen = QPen(QColor(0, 255, 255)) 
        pen.setWidth(3)
        pen.setStyle(Qt.DashLine)
        
        border.setPen(pen)
        border.setZValue(20000)
        
        self.current_scene.addItem(border)

    def generate_primitive_pixmap(self, data):
        w = int(data.get("width", 50))
        h = int(data.get("height", 50))
        c = data.get("color", [255, 255, 255])
        border = int(data.get("border_width", 0))
        
        pixmap = QPixmap(w, h)
        
        if border == 0:
            pixmap.fill(QColor(c[0], c[1], c[2]))
        else:
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            col = QColor(c[0], c[1], c[2])
            pen = QPen(col)
            pen.setWidth(border)
            pen.setJoinStyle(Qt.MiterJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            offset = border / 2
            painter.drawRect(QRectF(offset, offset, w - border, h - border))
            painter.end()
            
        return pixmap

    def draw_object_on_canvas(self, obj):
        """
        ## Description: 
            Creates the visual QGraphicsItem for an object based on its data.
        ## Parameters:
            - obj (dict): The data dictionary defining the object.
        ## Functionality:
            - Determines if the object is a 'Primitive' (draws a generated QPixmap) or a Sprite (loads an image).
            - Applies fallback colors (pink, cyan) if images are missing.
            - Sets Z-Index and position.
            - Wraps the graphic in a LevelObjectItem class (which handles drag & drop logic).
            - Adds the item to the current QGraphicsScene.
        """
        imgpath = obj.get("image_path", "None")
        pixmap = None
        obj_type = obj.get("type")
        if obj_type == ObjectTypes.PRIMITIVE:
            pixmap = self.generate_primitive_pixmap(obj)
            
            item = LevelObjectItem(pixmap, obj, self)
            
            x = obj.get("x", 0)
            y = obj.get("y", 0)
            
            item.setPos(x - pixmap.width()/2, y - pixmap.height()/2)
            
            z = int(obj.get("z_index", 0))
            item.setZValue(z)
            self.current_scene.addItem(item)
            return item
        
        if imgpath not in (None, "None", ""):
            full = os.path.join(self.base_path, imgpath)
            if os.path.exists(full):
                pixmap = QPixmap(full)

        if (not pixmap or pixmap.isNull()):
            pixmap = QPixmap(64, 64)
            if obj.get("type") == ObjectTypes.TRIGGER:
                pixmap.fill(QColor(255, 100, 255, 150))
            elif obj.get("type") == ObjectTypes.INTERACTABLE:
                pixmap.fill(QColor(100, 255, 255, 150))
            else:
                pixmap.fill(QColor(200, 200, 200, 150))

        try: factor = float(obj.get("resize_factor", 1))
        except: factor = 1
        if factor <= 0: factor = 1
        
        scaled = pixmap.scaled(int(pixmap.width()*factor), int(pixmap.height()*factor), Qt.KeepAspectRatio)
        item = LevelObjectItem(scaled, obj, self)
        
        item.ignore_movement = True
        item.setPos(obj.get("x", 0) - scaled.width()/2, obj.get("y", 0) - scaled.height()/2)
        item.ignore_movement = False
        
        z = int(obj.get("z_index", 0))
        if obj.get("is_ground"): z -= 1000
        item.setZValue(z)
        
        self.current_scene.addItem(item)
        return item

    def update_canvas_item(self, data, pixmap_item):
        """
        ## Description: 
            Refreshes the visuals of an existing item without destroying it.
        ## Parameters:
            - data (dict): The updated data source.
            - pixmap_item (LevelObjectItem): The graphical item to update.
        ## Functionality:
            - Re-generates the pixmap if color/size/image changed.
            - Updates position and Z-Index.
            - Re-calculates and redraws the Hitbox overlay (red rectangle).
            - Manages the visibility of the ResizeHandle (blue square) if the object is a Primitive.
        """
        if not pixmap_item: return
        
        imgpath = data.get("image_path", "None")
        pixmap = None

        obj_type = data.get("type")
        if obj_type == ObjectTypes.PRIMITIVE:
            pixmap = self.generate_primitive_pixmap(data)
        
        if imgpath not in (None, "None", ""):
            full = os.path.join(self.base_path, imgpath)
            if os.path.exists(full):
                pixmap = QPixmap(full)
        
        if (not pixmap or pixmap.isNull()):
            pixmap = QPixmap(64, 64)
            if data.get("type") == ObjectTypes.TRIGGER:
                pixmap.fill(QColor(255, 100, 255, 150))
            elif data.get("type") == ObjectTypes.INTERACTABLE:
                pixmap.fill(QColor(100, 255, 255, 150))
            else:
                pixmap.fill(QColor(200, 200, 200, 150))

        try: factor = float(data.get("resize_factor", 1))
        except: factor = 1
        if factor <= 0: factor = 1

        scaled = pixmap.scaled(int(pixmap.width()*factor), int(pixmap.height()*factor), Qt.KeepAspectRatio)
        pixmap_item.setPixmap(scaled)
        
        x = data.get("x", 0)
        y = data.get("y", 0)
        w = scaled.width()
        h = scaled.height()
        
        pixmap_item.ignore_movement = True
        pixmap_item.setPos(x - (w / 2), y - (h / 2))
        pixmap_item.ignore_movement = False
        
        z = int(data.get("z_index", 0))
        if data.get("is_ground"): z -= 1000
        pixmap_item.setZValue(z)
        
        if self.current_hitbox_item:
            self.current_scene.removeItem(self.current_hitbox_item)
            self.current_hitbox_item = None
        
        if not data.get("is_passable", False) or data.get("type") == ObjectTypes.TRIGGER:
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            sprite_x = x - (w / 2)
            sprite_y = y - (h / 2)
            hb_w = w + offset[2]
            hb_h = h + offset[3]
            
            self.current_hitbox_item = HitboxItem(QRectF(0, 0, hb_w, hb_h), data, pixmap_item, self)
            
            self.current_hitbox_item.ignore_movement = True
            self.current_hitbox_item.setPos(sprite_x + offset[0], sprite_y + offset[1])
            self.current_hitbox_item.ignore_movement = False
            self.current_hitbox_item.setZValue(9999)
            
            self.current_scene.addItem(self.current_hitbox_item)
            self.current_hitbox_item.add_resize_handle()
            
            if self.list_objects.currentItem() and self.list_objects.currentItem().data(Qt.UserRole) is data:
                self.current_hitbox_item.setSelected(True)

            if pixmap_item.isSelected():
                if data.get("type") == ObjectTypes.PRIMITIVE:
                    if not hasattr(pixmap_item, 'resize_handle') or not pixmap_item.resize_handle:
                        pixmap_item.create_primitive_handle()
                
                    if pixmap_item.resize_handle:
                        pixmap_item.resize_handle.update_position()
                else:
                    pixmap_item.remove_handle()

    def update_canvas_from_resize(self, data, item):
        if data.get("type") != ObjectTypes.PRIMITIVE: return
        
        pixmap = self.generate_primitive_pixmap(data)
        item.setPixmap(pixmap)
        
        w, h = pixmap.width(), pixmap.height()
        x, y = data.get("x", 0), data.get("y", 0)
        
        item.ignore_movement = False
        
        self.prop_width.blockSignals(True); self.prop_height.blockSignals(True)
        self.prop_width.setValue(w); self.prop_height.setValue(h)
        self.prop_width.blockSignals(False); self.prop_height.blockSignals(False)

    def on_object_selected(self, current, previous):
        if not current:
            self.disable_property_panel()
            return
        
        if not self._updating_selection_from_canvas:
            pixmap_item = current.data(Qt.UserRole + 1)
            if pixmap_item:
                self.current_scene.blockSignals(True)
                self.current_scene.clearSelection()
                pixmap_item.setSelected(True)
                if self.current_hitbox_item: self.current_hitbox_item.setSelected(True)
                self.current_scene.blockSignals(False)


        data = self.get_real_object_data()
        
        if data is None:
            self.disable_property_panel()
            return
        
        self.enable_property_panel()
        self.is_programmatic_change = True

        self.prop_id.setText(data.get("id", ""))
        self.prop_type.setCurrentText(data.get("type", ObjectTypes.OBSTACLE))
        self.prop_x.setValue(data.get("x", 0))
        self.prop_y.setValue(data.get("y", 0))
        self.prop_z_index.setValue(int(data.get("z_index", 0)))
        self.prop_reflection_offset.setValue(int(data.get("reflection_offset_y", 0)))
        
        self.prop_width.setValue(int(data.get("width", 50)))
        self.prop_height.setValue(int(data.get("height", 50)))
        self.prop_border_width.setValue(int(data.get("border_width", 0)))
        
        color = data.get("color", [255, 255, 255])
        if isinstance(color, list) and len(color) >= 3:
            self.prop_color_r.setValue(color[0])
            self.prop_color_g.setValue(color[1])
            self.prop_color_b.setValue(color[2])

        self.prop_image_path_combo.setCurrentText(data.get("image_path", "None"))
        try: rz = float(data.get("resize_factor", 1))
        except: rz = 1.0
        self.prop_resize_factor.setValue(rz)
        
        self.prop_is_passable.setChecked(data.get("is_passable", False))
        self.prop_starts_hidden.setChecked(data.get("starts_hidden", False))
        self.prop_is_ground.setChecked(data.get("is_ground", False))
        
        hb = data.get("collision_rect_offset", [0, 0, 0, 0])
        self.prop_hitbox_dx.setValue(hb[0])
        self.prop_hitbox_dy.setValue(hb[1])
        self.prop_hitbox_dw.setValue(hb[2])
        self.prop_hitbox_dh.setValue(hb[3])
        
        self.prop_anim_list.clear()
        self.prop_anim_list.addItems(data.get("animation_images", []))
        self.prop_anim_speed.setValue(data.get("animation_speed", 0.1))
        
        self.prop_flash_image_path_combo.setCurrentText(data.get("flash_image_path", "None"))
        self.prop_charge_sound_combo.setCurrentText(data.get("charge_sound_path", "None"))
        self.prop_used_image_path_combo.setCurrentText(data.get("used_image_path", "None"))
        self.prop_interaction_duration.setValue(int(data.get("interaction_duration", 60)))
            
        self.prop_trigger_action.setCurrentText(data.get("trigger_action", Actions.SET_FLAG))
        self.prop_trigger_params.setText(data.get("trigger_params", ""))

        self.list_trigger_sequence.clear()
        sequence = data.get("scripted_events", [])
        
        for step in sequence:
            action = step.get("action", Actions.WAIT)
            params = step.get("params", "")
            item_text = f"{action} ({params})"
            
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, step)
            self.list_trigger_sequence.addItem(list_item)
            
        self.group_step_detail.setEnabled(False)

        self.on_main_type_changed()
        self.update_image_preview()
        
        pixmap_item = current.data(Qt.UserRole + 1)
        
        if pixmap_item:
             self.update_canvas_item(data, pixmap_item)
        else:
             new_pix = self.draw_object_on_canvas(data)
             if new_pix:
                 current.setData(Qt.UserRole + 1, new_pix)
                 self.update_canvas_item(data, new_pix)
                 pixmap_item = new_pix
        
        if pixmap_item and data.get("type") == ObjectTypes.PRIMITIVE:
            pixmap_item.create_primitive_handle()
        elif pixmap_item:
            pixmap_item.remove_handle()

        self.is_programmatic_change = False

    def update_image_preview(self):
        path = self.prop_image_path_combo.currentText()
        if not path or path == "None":
            self.prop_image_preview.clear()
            self.prop_image_preview.setText("None")
            return
        full = os.path.join(self.base_path, path)
        pixmap = QPixmap(full)
        if pixmap.isNull(): self.prop_image_preview.setText("Error")
        else:
            scaled = pixmap.scaled(self.prop_image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.prop_image_preview.setPixmap(scaled)

    def add_animation_frame(self):
        start_dir = os.path.join(self.base_path, "assets")
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar", start_dir, "Images (*.png *.jpg)")
        if filepaths:
            for fp in filepaths:
                try: rel = os.path.relpath(fp, self.base_path).replace("\\", "/")
                except: rel = fp
                self.prop_anim_list.addItem(rel)
            
            anim_list = [self.prop_anim_list.item(i).text() for i in range(self.prop_anim_list.count())]

            obj_data = self.get_real_object_data()
            if obj_data:
                cmd = CmdPropertyChange(self, obj_data, 'animation_images', obj_data.get('animation_images', []), anim_list)
                self.undo_manager.push(cmd, execute_now=False)
                obj_data['animation_images'] = anim_list

    def remove_animation_frame(self):
        for item in self.prop_anim_list.selectedItems():
            self.prop_anim_list.takeItem(self.prop_anim_list.row(item))
        
        anim_list = [self.prop_anim_list.item(i).text() for i in range(self.prop_anim_list.count())]
        
        obj_data = self.get_real_object_data()
        if obj_data:
            cmd = CmdPropertyChange(self, obj_data, 'animation_images', obj_data.get('animation_images', []), anim_list)
            self.undo_manager.push(cmd, execute_now=False)
            obj_data['animation_images'] = anim_list

    def populate_sound_combos(self):
        sounds_path = os.path.join(self.base_path, "assets/sounds")
        sound_files = ["None"]
        
        if os.path.exists(sounds_path):
            for root, _, files in os.walk(sounds_path):
                for f in files:
                    if f.lower().endswith(AUDIO_EXTENSIONS):
                        rel = os.path.relpath(os.path.join(root, f), self.base_path)
                        sound_files.append(rel.replace("\\", "/"))
        
        self.prop_charge_sound_combo.blockSignals(True)
        self.prop_charge_sound_combo.clear()
        self.prop_charge_sound_combo.addItems(sound_files)
        self.prop_charge_sound_combo.blockSignals(False)

    def browse_audio_for_combo(self, combo_widget):
        start_dir = os.path.join(self.base_path, "assets/sounds")
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar Audio", start_dir, "Audio (*.wav *.mp3 *.ogg)")
        
        if filepath:
            try:
                rel_path = os.path.relpath(filepath, self.base_path).replace("\\", "/")
                if self.prop_charge_sound_combo.findText(rel_path) == -1:
                    self.prop_charge_sound_combo.addItem(rel_path)
                self.prop_charge_sound_combo.setCurrentText(rel_path)
            except: pass

    def save_sequence_changes(self):
        if self.is_programmatic_change: return
        
        obj_data = self.get_real_object_data()
        if not obj_data: return
        
        new_sequence = []
        for i in range(self.list_trigger_sequence.count()):
            item = self.list_trigger_sequence.item(i)
            step_data = item.data(Qt.UserRole)
            new_sequence.append(copy.deepcopy(step_data))
        
        old_sequence = obj_data.get("scripted_events", [])
        if new_sequence != old_sequence:
            cmd = CmdPropertyChange(self, obj_data, "scripted_events", old_sequence, new_sequence)
            self.undo_manager.push(cmd, execute_now=False)
            
            obj_data["scripted_events"] = new_sequence

    def add_sequence_step(self):
        new_step = {"action": Actions.WAIT, "params": "time=1.0"}
        
        item = QListWidgetItem(f"{Actions.WAIT} (time=1.0)")
        item.setData(Qt.UserRole, new_step)
        self.list_trigger_sequence.addItem(item)
        self.list_trigger_sequence.setCurrentItem(item)
        self.save_sequence_changes()

    def remove_sequence_step(self):
        row = self.list_trigger_sequence.currentRow()
        if row >= 0:
            self.list_trigger_sequence.takeItem(row)
            self.save_sequence_changes()

    def move_sequence_step(self, direction):
        row = self.list_trigger_sequence.currentRow()
        new_row = row + direction
        if 0 <= new_row < self.list_trigger_sequence.count():
            item = self.list_trigger_sequence.takeItem(row)
            self.list_trigger_sequence.insertItem(new_row, item)
            self.list_trigger_sequence.setCurrentRow(new_row)
            self.save_sequence_changes()

    def load_selected_step_to_ui(self):
        item = self.list_trigger_sequence.currentItem()
        self.group_step_detail.setEnabled(item is not None)
        
        if not item: return
        
        step_data = item.data(Qt.UserRole)
        
        self.is_programmatic_change = True
        self.prop_step_action.setCurrentText(step_data.get("action", Actions.WAIT))
        self.prop_step_params.setText(step_data.get("params", ""))
        self.is_programmatic_change = False

    def update_selected_step_data(self):
        if self.is_programmatic_change: return
        
        item = self.list_trigger_sequence.currentItem()
        if not item: return
        
        new_action = self.prop_step_action.currentText()
        new_params = self.prop_step_params.toPlainText()

        step_data = item.data(Qt.UserRole)
        step_data["action"] = new_action
        step_data["params"] = new_params
        item.setData(Qt.UserRole, step_data)
        
        item.setText(f"{new_action} ({new_params})")
        
        self.save_sequence_changes()

    def update_layers(self):
        show_obstacles = self.chk_layer_obstacles.isChecked()
        show_triggers = self.chk_layer_triggers.isChecked()
        show_interactables = self.chk_layer_interactables.isChecked()
        lock_ground = self.chk_lock_ground.isChecked()

        for item in self.current_scene.items():
            if isinstance(item, LevelObjectItem):
                obj_data = item.obj_data
                obj_type = obj_data.get("type")
                z_index = int(obj_data.get("z_index", 0))
                is_ground = obj_data.get("is_ground", False) or z_index < 0

                is_visible = True
                
                if obj_type == ObjectTypes.OBSTACLE and not show_obstacles:
                    is_visible = False
                elif obj_type == ObjectTypes.TRIGGER and not show_triggers:
                    is_visible = False
                elif obj_type == ObjectTypes.INTERACTABLE and not show_interactables:
                    is_visible = False
                
                item.setVisible(is_visible)

                if is_ground and lock_ground:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)
                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())