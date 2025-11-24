import sys
import json
import os
import time
import copy
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QListWidget, QInputDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QBrush, QColor, QPen, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QRectF, QPointF
from ui_editor import Ui_LevelEditor
from src.Game_Constants import MAPS

GAME_WIDTH = 1280
GAME_HEIGHT = 780
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
AUDIO_EXTENSIONS = ('.wav', '.mp3', '.ogg')

# --- Command system (UNDO/REDO) ---

class Command:
    def execute(self): pass
    def undo(self): pass

class UndoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, command, execute_now=True):
        self.undo_stack.append(command)
        self.redo_stack.clear()
        if execute_now: command.execute()

    def undo(self):
        if not self.undo_stack: return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        if not self.redo_stack: return
        cmd = self.redo_stack.pop()
        cmd.execute()
        self.undo_stack.append(cmd)

class CmdAddObject(Command):
    def __init__(self, editor, zone_key, obj_data):
        self.editor = editor
        self.zone_key = zone_key
        self.obj_data = obj_data
    def execute(self):
        if self.zone_key not in self.editor.current_data["zones"]:
            self.editor.current_data["zones"][self.zone_key] = []
        self.editor.current_data["zones"][self.zone_key].append(self.obj_data)
        self.editor.populate_views_for_current_zone()
        self.editor.select_object_by_id(self.obj_data["id"])
    def undo(self):
        zones = self.editor.current_data.get("zones", {})
        if self.zone_key in zones and self.obj_data in zones[self.zone_key]:
            zones[self.zone_key].remove(self.obj_data)
        self.editor.populate_views_for_current_zone()

class CmdDeleteObject(Command):
    def __init__(self, editor, zone_key, obj_data, index):
        self.editor = editor
        self.zone_key = zone_key
        self.obj_data = obj_data
        self.index = index
    def execute(self):
        zones = self.editor.current_data.get("zones", {})
        if self.zone_key in zones:
            if self.obj_data in zones[self.zone_key]:
                zones[self.zone_key].remove(self.obj_data)
        self.editor.populate_views_for_current_zone()
    def undo(self):
        if self.zone_key not in self.editor.current_data["zones"]:
            self.editor.current_data["zones"][self.zone_key] = []
        self.editor.current_data["zones"][self.zone_key].insert(self.index, self.obj_data)
        self.editor.populate_views_for_current_zone()
        self.editor.select_object_by_id(self.obj_data["id"])

class CmdPropertyChange(Command):
    def __init__(self, editor, obj_data, key, old_val, new_val):
        self.editor = editor
        self.obj_data = obj_data
        self.key = key
        self.old_val = old_val
        self.new_val = new_val
    def execute(self):
        self.obj_data[self.key] = self.new_val
        self.editor.refresh_ui_for_object(self.obj_data)
    def undo(self):
        self.obj_data[self.key] = self.old_val
        self.editor.refresh_ui_for_object(self.obj_data)

class CmdTransform(Command):
    def __init__(self, editor, obj_data, old_pos, new_pos, old_offset, new_offset):
        self.editor = editor
        self.obj_data = obj_data
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.old_offset = old_offset
        self.new_offset = new_offset
    def execute(self):
        self.obj_data['x'] = self.new_pos[0]
        self.obj_data['y'] = self.new_pos[1]
        self.obj_data['collision_rect_offset'] = self.new_offset
        self.editor.refresh_ui_for_object(self.obj_data)
    def undo(self):
        self.obj_data['x'] = self.old_pos[0]
        self.obj_data['y'] = self.old_pos[1]
        self.obj_data['collision_rect_offset'] = self.old_offset
        self.editor.refresh_ui_for_object(self.obj_data)

# --- VISUALS ---
class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent_hitbox, editor_ref):
        super().__init__(0, 0, 10, 10, parent_hitbox)
        self.parent_hitbox = parent_hitbox
        self.editor = editor_ref
        self.setBrush(QBrush(QColor(0, 0, 255, 200)))
        self.setPen(QPen(Qt.NoPen))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsSelectable)
        self.update_position_from_parent()
    def update_position_from_parent(self):
        rect = self.parent_hitbox.rect()
        self.setPos(rect.width() - 5, rect.height() - 5)
    def mousePressEvent(self, event):
        data = self.parent_hitbox.obj_data
        self.start_offset = copy.deepcopy(data.get('collision_rect_offset', [0,0,0,0]))
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        data = self.parent_hitbox.obj_data
        end_offset = data.get('collision_rect_offset', [0,0,0,0])
        if self.start_offset != end_offset and self.editor:
            cmd = CmdTransform(self.editor, data, (data['x'], data['y']), (data['x'], data['y']), self.start_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if self.parent_hitbox.ignore_movement: return super().itemChange(change, value)
            new_pos = value
            new_width = max(5, new_pos.x() + 5)
            new_height = max(5, new_pos.y() + 5)
            self.parent_hitbox.setRect(0, 0, new_width, new_height)
            data = self.parent_hitbox.obj_data
            current_offset = data.get('collision_rect_offset', [0,0,0,0])
            pixmap_item = self.parent_hitbox.parent_sprite
            if not pixmap_item.pixmap() or pixmap_item.pixmap().isNull(): return super().itemChange(change, value)
            scale = pixmap_item.scale()
            orig_w = pixmap_item.pixmap().width() * scale
            orig_h = pixmap_item.pixmap().height() * scale
            new_dw = int(new_width - orig_w)
            new_dh = int(new_height - orig_h)
            data['collision_rect_offset'] = [current_offset[0], current_offset[1], new_dw, new_dh]
            if self.editor: self.editor.sync_hitbox_size_ui(new_dw, new_dh)
        return super().itemChange(change, value)

class HitboxItem(QGraphicsRectItem):
    def __init__(self, rect, obj_data, parent_sprite_item, editor_ref):
        super().__init__(rect)
        self.obj_data = obj_data
        self.parent_sprite = parent_sprite_item
        self.editor = editor_ref
        self.resize_handle = None
        self.ignore_movement = False
        self.setBrush(QBrush(QColor(255, 0, 0, 80)))
        self.setPen(QPen(QColor(255, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
    def add_resize_handle(self):
        self.resize_handle = ResizeHandle(self, self.editor)
    def mousePressEvent(self, event):
        self.start_pos_offset = copy.deepcopy(self.obj_data.get('collision_rect_offset', [0,0,0,0]))
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        end_offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
        if self.start_pos_offset != end_offset and self.editor:
            cmd = CmdTransform(self.editor, self.obj_data, (self.obj_data['x'], self.obj_data['y']), (self.obj_data['x'], self.obj_data['y']), self.start_pos_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene() and self.parent_sprite:
            if self.ignore_movement: return super().itemChange(change, value)
            sprite_pos = self.parent_sprite.pos()
            new_hitbox_pos = value
            dx = int(new_hitbox_pos.x() - sprite_pos.x())
            dy = int(new_hitbox_pos.y() - sprite_pos.y())
            current_offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
            self.obj_data['collision_rect_offset'] = [dx, dy, current_offset[2], current_offset[3]]
            if self.editor: self.editor.sync_hitbox_pos_ui(dx, dy)
        return super().itemChange(change, value)

class LevelObjectItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, obj_data, editor_ref):
        super().__init__(pixmap)
        self.obj_data = obj_data
        self.editor = editor_ref
        self.ignore_movement = False
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
    def mousePressEvent(self, event):
        self.start_x = self.obj_data.get('x', 0)
        self.start_y = self.obj_data.get('y', 0)
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        end_x = self.obj_data.get('x', 0)
        end_y = self.obj_data.get('y', 0)
        if (self.start_x != end_x or self.start_y != end_y) and self.editor:
            offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
            cmd = CmdTransform(self.editor, self.obj_data, (self.start_x, self.start_y), (end_x, end_y), offset, offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if self.ignore_movement: return super().itemChange(change, value)
            new_pos = value
            if self.editor and self.editor.chk_grid_snap.isChecked():
                grid_size = self.editor.spin_grid_size.value()
                if grid_size > 0:
                    snapped_x = round(new_pos.x() / grid_size) * grid_size
                    snapped_y = round(new_pos.y() / grid_size) * grid_size
                    new_pos = QPointF(snapped_x, snapped_y)
                    if change == QGraphicsItem.ItemPositionChange:
                        scale = self.scale()
                        w = self.pixmap().width() * scale
                        h = self.pixmap().height() * scale
                        new_center_x = int(new_pos.x() + w / 2)
                        new_center_y = int(new_pos.y() + h / 2)
                        self.obj_data['x'] = new_center_x
                        self.obj_data['y'] = new_center_y
                        if self.editor: self.editor.sync_obj_pos_ui(new_center_x, new_center_y)
                        return new_pos 
            scale = self.scale()
            w = self.pixmap().width() * scale
            h = self.pixmap().height() * scale
            new_center_x = int(new_pos.x() + w / 2)
            new_center_y = int(new_pos.y() + h / 2)
            self.obj_data['x'] = new_center_x
            self.obj_data['y'] = new_center_y
            if self.editor: self.editor.sync_obj_pos_ui(new_center_x, new_center_y)
        return super().itemChange(change, value)

# --- EDITOR ---
class LevelEditor(QMainWindow, Ui_LevelEditor):
    def __init__(self):
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
        self.all_image_combos = [self.prop_image_path_combo, self.prop_flash_image_path_combo, self.data_image_path_combo, self.prop_used_image_path_combo]

        self.action_new_map.triggered.connect(self.create_new_json_from_map)
        self.action_load_json.triggered.connect(self.load_json)
        self.action_save_json.triggered.connect(self.save_json)
        self.btn_add_object.clicked.connect(self.add_new_object)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)
        self.combo_zone_selector.currentIndexChanged.connect(self.populate_views_for_current_zone)
        
        self.list_objects.currentItemChanged.connect(self.on_object_selected)

        self.prop_x.valueChanged.connect(lambda v: self.on_property_changed('x', v))
        self.prop_y.valueChanged.connect(lambda v: self.on_property_changed('y', v))
        self.prop_z_index.valueChanged.connect(lambda v: self.on_property_changed('z_index', v))
        self.prop_reflection_offset.valueChanged.connect(lambda v: self.on_property_changed('reflection_offset_y', v))
        self.prop_resize_factor.valueChanged.connect(lambda v: self.on_property_changed('resize_factor', v))
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
        self.prop_interaction_type.currentTextChanged.connect(lambda v: self.on_property_changed('interaction_type', v))
        self.data_image_path_combo.currentTextChanged.connect(lambda v: self.on_property_changed('interaction_data', v))
        self.prop_is_passable.stateChanged.connect(lambda v: self.on_property_changed('is_passable', bool(v)))
        self.prop_starts_hidden.stateChanged.connect(lambda v: self.on_property_changed('starts_hidden', bool(v)))
        self.prop_is_ground.stateChanged.connect(lambda v: self.on_property_changed('is_ground', bool(v)))
        self.data_note_text.textChanged.connect(self.on_note_text_changed)
        self.prop_trigger_condition.currentTextChanged.connect(lambda v: self.on_property_changed('trigger_condition', v))
        self.prop_trigger_action.currentTextChanged.connect(lambda v: self.on_property_changed('trigger_action', v))
        self.prop_trigger_params.textChanged.connect(self.on_trigger_params_changed)
        self.btn_anim_add.clicked.connect(self.add_animation_frame)
        self.btn_anim_remove.clicked.connect(self.remove_animation_frame)
        self.prop_image_path_combo.currentTextChanged.connect(self.update_image_preview)
        self.prop_type.currentTextChanged.connect(self.on_main_type_changed)
        self.prop_interaction_type.currentTextChanged.connect(self.on_interaction_type_changed)
        self.btn_browse_image.clicked.connect(lambda: self.browse_file_for_combo(self.prop_image_path_combo))
        self.btn_browse_flash.clicked.connect(lambda: self.browse_file_for_combo(self.prop_flash_image_path_combo))
        self.btn_browse_charge.clicked.connect(lambda: self.browse_audio_for_combo(self.prop_charge_sound_combo))
        self.btn_browse_used.clicked.connect(lambda: self.browse_file_for_combo(self.prop_used_image_path_combo))
        self.btn_browse_data.clicked.connect(lambda: self.browse_file_for_combo(self.data_image_path_combo))
        self.shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut_up.activated.connect(lambda: self.navigate_zone(0, -1))
        self.shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut_down.activated.connect(lambda: self.navigate_zone(0, 1))
        self.shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut_left.activated.connect(lambda: self.navigate_zone(-1, 0))
        self.shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut_right.activated.connect(lambda: self.navigate_zone(1, 0))
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(self.copy_object)
        self.shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)
        self.shortcut_paste.activated.connect(self.paste_object)
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_undo.activated.connect(self.perform_undo)
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.shortcut_redo.activated.connect(self.perform_redo)
        self.combo_map_select.addItems(list(MAPS.keys()))
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
        current = self.list_objects.currentItem()
        if current and current.data(Qt.UserRole) is obj_data:
            self.is_programmatic_change = True
            
            self.prop_x.setValue(obj_data.get('x', 0))
            self.prop_y.setValue(obj_data.get('y', 0))
            self.prop_z_index.setValue(int(obj_data.get('z_index', 0)))
            self.prop_reflection_offset.setValue(int(obj_data.get('reflection_offset_y', 0)))
            

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

            self.prop_interaction_type.setCurrentText(obj_data.get('interaction_type', 'None'))
            
            itype = obj_data.get('interaction_type', 'None')
            idata = obj_data.get('interaction_data', "")
            
            if itype == "Note":
                if isinstance(idata, list):
                    self.data_note_text.setText("\n".join(idata))
                else:
                    self.data_note_text.setText(str(idata))
            elif itype == "Image":
                self.data_image_path_combo.setCurrentText(str(idata))

            self.prop_trigger_condition.setCurrentText(obj_data.get("trigger_condition", "OnEnter"))
            self.prop_trigger_action.setCurrentText(obj_data.get("trigger_action", "SetFlag"))
            self.prop_trigger_params.setText(obj_data.get("trigger_params", ""))
            
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
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key: return
        new_id = f"obj_{int(time.time())}"
        new_obj_data = {
            "id": new_id, "type": "Obstacle", "x": GAME_WIDTH // 2, "y": GAME_HEIGHT // 2, "z_index": 0,
            "image_path": "None", "resize_factor": 1.0, "is_passable": False, "starts_hidden": False, "is_ground": False,
            "collision_rect_offset": [0, 0, 0, 0], "animation_images": [], "animation_speed": 0.1,
            "flash_image_path": "None", "charge_sound_path": "None", "used_image_path": "None", "interaction_type": "None", "interaction_data": "",
            "trigger_condition": "OnEnter", "trigger_action": "SetFlag", "trigger_params": ""
        }
        cmd = CmdAddObject(self, current_zone_key, new_obj_data)
        self.undo_manager.push(cmd, execute_now=True)

    def delete_selected_object(self):
        obj_data = self.get_real_object_data()
        if not obj_data:
            return

        current_item = self.list_objects.currentItem()
        zone = self.combo_zone_selector.currentText()
        index = self.list_objects.row(current_item)
        
        cmd = CmdDeleteObject(self, zone, obj_data, index)
        self.undo_manager.push(cmd, execute_now=True)
    def get_real_object_data(self):
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
        if self.is_programmatic_change: return
        obj_data = self.get_real_object_data()
        if not obj_data: return
        
        current_item = self.list_objects.currentItem()
        
        old_value = obj_data.get(key)
        if old_value == new_value: return

        cmd = CmdPropertyChange(self, obj_data, key, old_value, new_value)
        self.undo_manager.push(cmd, execute_now=False)
        
        obj_data[key] = new_value
        
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

    def on_note_text_changed(self):
        if self.is_programmatic_change: return
        
        obj_data = self.get_real_object_data()
        if not obj_data: return
        
        obj_data['interaction_data'] = self.data_note_text.toPlainText()

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
            # Crear nueva zona vacía si es válida en el mapa pero no existe en el JSON
            self.current_data["zones"][target] = []
            self.combo_zone_selector.addItem(target)
            self.combo_zone_selector.setCurrentText(target)

    def on_scene_selection_changed(self):
        if self.list_objects.signalsBlocked(): return
        selected_items = self.current_scene.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        target_data = None
        if isinstance(item, LevelObjectItem): target_data = item.obj_data
        elif isinstance(item, HitboxItem): target_data = item.obj_data
        elif isinstance(item, ResizeHandle): target_data = item.parent_hitbox.obj_data
        if target_data:
            tid = target_data.get("id")
            for i in range(self.list_objects.count()):
                li = self.list_objects.item(i)
                if li.data(Qt.UserRole).get("id") == tid:
                    self._updating_selection_from_canvas = True 
                    self.list_objects.setCurrentItem(li)
                    self.list_objects.scrollToItem(li)
                    self._updating_selection_from_canvas = False
                    self.enable_property_panel()
                    break

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
        self.group_interaction.setEnabled(current_type in ["Interactable", "Trigger"])
        self.group_animation.setEnabled(True)
        if current_type == "Interactable": self.prop_main_stack.setCurrentIndex(0)
        elif current_type == "Trigger": self.prop_main_stack.setCurrentIndex(1)
        else: self.prop_main_stack.setCurrentIndex(0)

    def on_interaction_type_changed(self):
        combo_text = self.prop_interaction_type.currentText()
        idx = 0
        if combo_text == "Note": idx = 0
        elif combo_text == "Image": idx = 1
        elif combo_text == "Door": idx = 2
        self.prop_interaction_data_stack.setCurrentIndex(idx)

    def create_new_json_from_map(self):
        """
        Creates a new JSON file with every zone empty, based on the matrix of the map
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
                try: obj["resize_factor"] = float(obj.get("resize_factor", 1))
                except: obj["resize_factor"] = 1.0
                try: obj["z_index"] = int(obj.get("z_index", 0))
                except: obj["z_index"] = 0
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

    def draw_game_border(self):
        border = QGraphicsRectItem(0, 0, GAME_WIDTH, GAME_HEIGHT)
        
        pen = QPen(QColor(0, 255, 255)) 
        pen.setWidth(3)
        pen.setStyle(Qt.DashLine)
        
        border.setPen(pen)
        border.setZValue(20000)
        
        self.current_scene.addItem(border)

    def draw_object_on_canvas(self, obj):
        imgpath = obj.get("image_path", "None")
        pixmap = None
        
        if imgpath not in (None, "None", ""):
            full = os.path.join(self.base_path, imgpath)
            if os.path.exists(full):
                pixmap = QPixmap(full)

        if (not pixmap or pixmap.isNull()):
            pixmap = QPixmap(64, 64)
            if obj.get("type") == "Trigger":
                pixmap.fill(QColor(255, 100, 255, 150))
            elif obj.get("type") == "Interactable":
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
        if not pixmap_item: return
        
        imgpath = data.get("image_path", "None")
        pixmap = None
        
        if imgpath not in (None, "None", ""):
            full = os.path.join(self.base_path, imgpath)
            if os.path.exists(full):
                pixmap = QPixmap(full)
        
        if (not pixmap or pixmap.isNull()):
            pixmap = QPixmap(64, 64)
            if data.get("type") == "Trigger":
                pixmap.fill(QColor(255, 100, 255, 150))
            elif data.get("type") == "Interactable":
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
        
        if not data.get("is_passable", False) or data.get("type") == "Trigger":
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
        self.prop_type.setCurrentText(data.get("type", "Obstacle"))
        self.prop_x.setValue(data.get("x", 0))
        self.prop_y.setValue(data.get("y", 0))
        self.prop_z_index.setValue(int(data.get("z_index", 0)))
        self.prop_reflection_offset.setValue(int(data.get("reflection_offset_y", 0)))
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
        self.prop_interaction_type.setCurrentText(data.get("interaction_type", "None"))
        itype = data.get("interaction_type", "None")
        idata = data.get("interaction_data", "")
        if itype == "Note": self.data_note_text.setText(str(idata))
        elif itype == "Image": self.data_image_path_combo.setCurrentText(str(idata))
        
        self.prop_trigger_condition.setCurrentText(data.get("trigger_condition", "OnEnter"))
        self.prop_trigger_action.setCurrentText(data.get("trigger_action", "SetFlag"))
        self.prop_trigger_params.setText(data.get("trigger_params", ""))

        self.on_main_type_changed()
        self.on_interaction_type_changed()
        self.update_image_preview()
        
        pixmap_item = current.data(Qt.UserRole + 1)
        if pixmap_item:
            self.update_canvas_item(data, pixmap_item)
        else:
            new_pix = self.draw_object_on_canvas(data)
            if new_pix:
                current.setData(Qt.UserRole + 1, new_pix)
                self.update_canvas_item(data, new_pix)
        
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())