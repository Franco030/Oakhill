import sys
import json
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QListWidget, QFormLayout,
    QWidget, QHBoxLayout, QSizePolicy
)
from PySide6.QtGui import QPixmap, QBrush, QColor, QPen, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QRectF, QPointF
from ui_editor import Ui_LevelEditor
from src.Game_Constants import WORLD_MAP_LEVEL

GAME_WIDTH = 1280
GAME_HEIGHT = 780
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")

# --- CLASES VISUALES ---

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

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if self.parent_hitbox.ignore_movement:
                return super().itemChange(change, value)

            new_pos = value
            new_width = max(5, new_pos.x() + 5)
            new_height = max(5, new_pos.y() + 5)
            
            self.parent_hitbox.setRect(0, 0, new_width, new_height)
            
            data = self.parent_hitbox.obj_data
            current_offset = data.get('collision_rect_offset', [0,0,0,0])
            
            pixmap_item = self.parent_hitbox.parent_sprite
            scale = pixmap_item.scale()
            if pixmap_item.pixmap().isNull(): return super().itemChange(change, value)

            orig_w = pixmap_item.pixmap().width() * scale
            orig_h = pixmap_item.pixmap().height() * scale
            
            new_dw = int(new_width - orig_w)
            new_dh = int(new_height - orig_h)
            
            data['collision_rect_offset'] = [current_offset[0], current_offset[1], new_dw, new_dh]

            if self.editor:
                self.editor.sync_hitbox_size_ui(new_dw, new_dh)
                
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

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene() and self.parent_sprite:
            if self.ignore_movement:
                return super().itemChange(change, value)

            sprite_pos = self.parent_sprite.pos()
            new_hitbox_pos = value
            
            dx = int(new_hitbox_pos.x() - sprite_pos.x())
            dy = int(new_hitbox_pos.y() - sprite_pos.y())
            
            current_offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
            self.obj_data['collision_rect_offset'] = [dx, dy, current_offset[2], current_offset[3]]
            
            if self.editor:
                self.editor.sync_hitbox_pos_ui(dx, dy)

        return super().itemChange(change, value)


class LevelObjectItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, obj_data, editor_ref):
        super().__init__(pixmap)
        self.obj_data = obj_data
        self.editor = editor_ref
        self.ignore_movement = False
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if self.ignore_movement:
                return super().itemChange(change, value)

            new_pos = value
            scale = self.scale()
            w = self.pixmap().width() * scale
            h = self.pixmap().height() * scale
            
            new_center_x = int(new_pos.x() + w / 2)
            new_center_y = int(new_pos.y() + h / 2)

            self.obj_data['x'] = new_center_x
            self.obj_data['y'] = new_center_y

            if self.editor:
                self.editor.sync_obj_pos_ui(new_center_x, new_center_y)
                
        return super().itemChange(change, value)


# --- EDITOR PRINCIPAL ---

class LevelEditor(QMainWindow, Ui_LevelEditor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.prop_is_ground = QCheckBox(self.properties_box)
        self.prop_is_ground.setObjectName("prop_is_ground")
        self.prop_is_ground.setText("Es Suelo (Fondo)")
        self.horizontalLayout_7.addWidget(self.prop_is_ground)

        self.label_z = QLabel("Z-Order (Prioridad):", self.properties_box)
        self.prop_z_index = QSpinBox(self.properties_box)
        self.prop_z_index.setRange(-100, 100) 
        self.prop_z_index.setValue(0)
        self.prop_z_index.setToolTip("Mayor número = Más al frente. 0 = Automático por Y.")
        
        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_z)
        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.prop_z_index)

        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.current_data = {"zones": {}}
        self.image_paths = []

        self.current_scene = QGraphicsScene()
        self.canvas_view.setScene(self.current_scene)
        self.current_scene.setSceneRect(0, 0, GAME_WIDTH, GAME_HEIGHT)
        self.current_scene.setBackgroundBrush(QBrush(QColor(50, 50, 50)))
        
        self.current_scene.selectionChanged.connect(self.on_scene_selection_changed)

        self.current_hitbox_item = None
        self._updating_selection_from_canvas = False 

        self.all_image_combos = [
            self.prop_image_path_combo, self.prop_flash_image_path_combo, self.data_image_path_combo
        ]

        # --- MEJORA: Inyectar botones de "Examinar..." ---
        self.setup_browse_button(self.formLayout, 3, self.prop_image_path_combo)
        self.setup_browse_button(self.formLayout_2, 1, self.prop_flash_image_path_combo)
        
        # Para el data_image_path_combo (que ya está en un HBox), solo añadimos el botón
        self.btn_browse_data = QPushButton("...")
        self.btn_browse_data.setFixedWidth(30)
        self.btn_browse_data.clicked.connect(lambda: self.browse_file_for_combo(self.data_image_path_combo))
        self.horizontalLayout_2.addWidget(self.btn_browse_data)
        # -------------------------------------------------

        self.action_load_json.triggered.connect(self.load_json)
        self.action_save_json.triggered.connect(self.save_json)
        self.btn_add_object.clicked.connect(self.add_new_object)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)
        self.combo_zone_selector.currentIndexChanged.connect(self.populate_views_for_current_zone)
        self.list_objects.currentItemChanged.connect(self.on_object_selected)

        self.prop_x.valueChanged.connect(self.on_property_changed)
        self.prop_y.valueChanged.connect(self.on_property_changed)
        self.prop_z_index.valueChanged.connect(self.on_property_changed)
        self.prop_resize_factor.valueChanged.connect(self.on_property_changed)
        self.prop_hitbox_dx.valueChanged.connect(self.on_property_changed)
        self.prop_hitbox_dy.valueChanged.connect(self.on_property_changed)
        self.prop_hitbox_dw.valueChanged.connect(self.on_property_changed)
        self.prop_hitbox_dh.valueChanged.connect(self.on_property_changed)
        self.prop_anim_speed.valueChanged.connect(self.on_property_changed)
        self.prop_type.currentTextChanged.connect(self.on_property_changed)
        self.prop_image_path_combo.currentTextChanged.connect(self.on_property_changed)
        self.prop_flash_image_path_combo.currentTextChanged.connect(self.on_property_changed)
        self.prop_interaction_type.currentTextChanged.connect(self.on_property_changed)
        self.data_image_path_combo.currentTextChanged.connect(self.on_property_changed)
        self.prop_is_passable.stateChanged.connect(self.on_property_changed)
        self.prop_starts_hidden.stateChanged.connect(self.on_property_changed)
        self.prop_is_ground.stateChanged.connect(self.on_property_changed)
        self.data_note_text.textChanged.connect(self.on_property_changed)
        self.btn_anim_add.clicked.connect(self.add_animation_frame)
        self.btn_anim_remove.clicked.connect(self.remove_animation_frame)

        self.prop_image_path_combo.currentTextChanged.connect(self.update_image_preview)
        self.prop_type.currentTextChanged.connect(self.on_main_type_changed)
        self.prop_interaction_type.currentTextChanged.connect(self.on_interaction_type_changed)
        
        self.shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut_up.activated.connect(lambda: self.navigate_zone(0, -1))
        self.shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut_down.activated.connect(lambda: self.navigate_zone(0, 1))
        self.shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut_left.activated.connect(lambda: self.navigate_zone(-1, 0))
        self.shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut_right.activated.connect(lambda: self.navigate_zone(1, 0))

        self.populate_image_combos()
        self.disable_property_panel()

    # --- SISTEMA DE SELECCIÓN DE ARCHIVOS ---
    
    def setup_browse_button(self, form_layout, row, combo_widget):
        """
        Reemplaza un combobox en un FormLayout con un contenedor que tiene [ComboBox] + [Botón]
        """
        # 1. Crear contenedor y layout horizontal
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)
        
        # 2. Crear el botón de examinar
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(30)
        btn_browse.setToolTip("Examinar archivos...")
        btn_browse.clicked.connect(lambda: self.browse_file_for_combo(combo_widget))

        # 3. Sacar el combo del layout original y ponerlo en el nuestro
        # (Qt a veces es quisquilloso al mover widgets, pero esto suele funcionar)
        form_layout.removeWidget(combo_widget)
        
        h_layout.addWidget(combo_widget)
        h_layout.addWidget(btn_browse)
        
        # 4. Poner el contenedor en el FormLayout original
        form_layout.setWidget(row, QFormLayout.FieldRole, container)

    def browse_file_for_combo(self, combo_widget):
        """Abre el explorador, obtiene la ruta relativa y la pone en el combo."""
        start_dir = os.path.join(self.base_path, "assets")
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", start_dir, "Images (*.png *.jpg *.jpeg)"
        )
        
        if filepath:
            try:
                # Intentar obtener ruta relativa a la carpeta del proyecto
                rel_path = os.path.relpath(filepath, self.base_path)
                # Normalizar slashes para que sea compatible con Windows/Mac/Linux
                clean_path = rel_path.replace("\\", "/")
                
                # Añadir al combo si no existe y seleccionarlo
                if clean_path not in [combo_widget.itemText(i) for i in range(combo_widget.count())]:
                    combo_widget.addItem(clean_path)
                
                combo_widget.setCurrentText(clean_path)
                
                # IMPORTANTE: Forzar actualización de propiedades
                self.on_property_changed()
                
            except ValueError:
                print("Error: El archivo seleccionado debe estar dentro de la carpeta del proyecto.")

    # --- NAVEGACIÓN ---
    def navigate_zone(self, dx, dy):
        focus_widget = QApplication.focusWidget()
        if isinstance(focus_widget, (QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox)):
            return
        
        current_text = self.combo_zone_selector.currentText()
        if not current_text: return

        try:
            content = current_text.replace("(", "").replace(")", "")
            parts = content.split(",")
            current_y = int(parts[0])
            current_x = int(parts[1])
        except: return

        new_y = current_y + dy
        new_x = current_x + dx
        
        if new_y < 0 or new_y >= len(WORLD_MAP_LEVEL) or new_x < 0 or new_x >= len(WORLD_MAP_LEVEL[0]):
            print(f"Bloqueado: Fuera de límites ({new_y}, {new_x})")
            return
        if WORLD_MAP_LEVEL[new_y][new_x] == 0:
            print(f"Bloqueado: Zona inválida (0) en el mapa.")
            return

        target_zone_key = f"({new_y}, {new_x})"
        index = self.combo_zone_selector.findText(target_zone_key)
        if index != -1:
            self.combo_zone_selector.setCurrentIndex(index)
        else:
            print(f"Creando nueva zona válida: {target_zone_key}")
            self.current_data["zones"][target_zone_key] = []
            self.combo_zone_selector.addItem(target_zone_key)
            self.combo_zone_selector.setCurrentText(target_zone_key)


    # --- SINCRONIZACIÓN ---

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
            target_id = target_data.get("id")
            for i in range(self.list_objects.count()):
                list_item = self.list_objects.item(i)
                item_data = list_item.data(Qt.UserRole)
                if item_data.get("id") == target_id:
                    self._updating_selection_from_canvas = True 
                    self.list_objects.setCurrentItem(list_item)
                    self.list_objects.scrollToItem(list_item)
                    self._updating_selection_from_canvas = False
                    self.enable_property_panel()
                    break

    def sync_obj_pos_ui(self, x, y):
        self.prop_x.blockSignals(True)
        self.prop_y.blockSignals(True)
        self.prop_x.setValue(x)
        self.prop_y.setValue(y)
        self.prop_x.blockSignals(False)
        self.prop_y.blockSignals(False)
        self.update_hitbox_position_only()

    def sync_hitbox_pos_ui(self, dx, dy):
        self.prop_hitbox_dx.blockSignals(True)
        self.prop_hitbox_dy.blockSignals(True)
        self.prop_hitbox_dx.setValue(dx)
        self.prop_hitbox_dy.setValue(dy)
        self.prop_hitbox_dx.blockSignals(False)
        self.prop_hitbox_dy.blockSignals(False)

    def sync_hitbox_size_ui(self, dw, dh):
        self.prop_hitbox_dw.blockSignals(True)
        self.prop_hitbox_dh.blockSignals(True)
        self.prop_hitbox_dw.setValue(dw)
        self.prop_hitbox_dh.setValue(dh)
        self.prop_hitbox_dw.blockSignals(False)
        self.prop_hitbox_dh.blockSignals(False)

    def update_hitbox_position_only(self):
        if not self.current_hitbox_item or not self.list_objects.currentItem(): return
        self.current_hitbox_item.ignore_movement = True
        pixmap_item = self.list_objects.currentItem().data(Qt.UserRole + 1)
        if pixmap_item:
            data = self.list_objects.currentItem().data(Qt.UserRole)
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            sprite_pos = pixmap_item.pos()
            self.current_hitbox_item.setPos(sprite_pos.x() + offset[0], sprite_pos.y() + offset[1])
        self.current_hitbox_item.ignore_movement = False

    # --- MÉTODOS UI ---

    def _block_all_property_signals(self, block: bool):
        parent_widget = self.scrollAreaWidgetContents
        types_to_block = (QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit, QListWidget)
        for widget_type in types_to_block:
            for widget in parent_widget.findChildren(widget_type):
                widget.blockSignals(block)

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
        is_interactable = self.prop_type.currentText() == "Interactable"
        self.group_interaction.setEnabled(is_interactable)
        self.group_animation.setEnabled(True)

    def on_interaction_type_changed(self):
        combo_text = self.prop_interaction_type.currentText()
        idx = 0
        if combo_text == "Note": idx = 0
        elif combo_text == "Image": idx = 1
        elif combo_text == "Door": idx = 2
        self.prop_interaction_data_stack.setCurrentIndex(idx)

    # --- CARGA Y GUARDADO ---

    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Cargar JSON", self.base_path, "JSON (*.json)")
        if not filepath: return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
        except Exception as e:
            print(f"Error: {e}")
            self.current_data = {"zones": {}}
        self.combo_zone_selector.blockSignals(True)
        self.combo_zone_selector.clear()
        self.combo_zone_selector.addItems(list(self.current_data.get("zones", {}).keys()))
        self.combo_zone_selector.blockSignals(False)
        self.populate_views_for_current_zone()

    def sanitize_before_save(self):
        zones = self.current_data.get("zones", {})
        for zone_key, objects in zones.items():
            for obj in objects:
                for k in ("image_path", "flash_image_path"):
                    if obj.get(k) in (None, "None"): obj[k] = ""
                try: obj["resize_factor"] = float(obj.get("resize_factor", 1))
                except: obj["resize_factor"] = 1.0
                try: obj["z_index"] = int(obj.get("z_index", 0))
                except: obj["z_index"] = 0
                
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
                else:
                    obj["interaction_data"] = ""

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", self.base_path, "JSON (*.json)")
        if not filepath: return
        try: self.sanitize_before_save()
        except Exception as e: print(f"Error sanitizando: {e}")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.current_data, f, indent=4, ensure_ascii=False)
            print("Guardado exitoso.")
        except Exception as e: print(f"Error al guardar: {e}")

    # --- VISTAS ---

    def populate_image_combos(self):
        self.image_paths = ["None"]
        for folder in ["assets/images", "assets/animations"]:
            full = os.path.join(self.base_path, folder)
            if not os.path.exists(full): continue
            for root, _, files in os.walk(full):
                for f in files:
                    if f.lower().endswith(IMAGE_EXTENSIONS):
                        rel = os.path.relpath(os.path.join(root, f), self.base_path)
                        self.image_paths.append(rel.replace("\\", "/"))
        for combo in self.all_image_combos:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(self.image_paths)
            combo.blockSignals(False)

    def populate_views_for_current_zone(self):
        self.list_objects.clear()
        self.current_scene.clear()
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

    def draw_object_on_canvas(self, obj):
        imgpath = obj.get("image_path", "None")
        if imgpath in (None, "None", ""): return None
        full = os.path.join(self.base_path, imgpath)
        if not os.path.exists(full): return None
        pixmap = QPixmap(full)
        if pixmap.isNull(): return None
        try: factor = float(obj.get("resize_factor", 1))
        except: factor = 1
        if factor <= 0: factor = 1
        scaled = pixmap.scaled(int(pixmap.width()*factor), int(pixmap.height()*factor), Qt.KeepAspectRatio)
        item = LevelObjectItem(scaled, obj, self)
        item.ignore_movement = True
        item.setPos(obj.get("x", 0) - scaled.width()/2, obj.get("y", 0) - scaled.height()/2)
        item.ignore_movement = False
        
        z_val = int(obj.get("z_index", 0))
        if obj.get("is_ground"): z_val -= 1000
        item.setZValue(z_val)
        
        self.current_scene.addItem(item)
        return item

    def update_canvas_item(self, data, pixmap_item):
        if not pixmap_item: return
        imgpath = data.get("image_path", "None")
        should_hide = imgpath in (None, "None", "")
        if not should_hide:
            full = os.path.join(self.base_path, imgpath)
            if not os.path.exists(full): should_hide = True
            else:
                pixmap = QPixmap(full)
                if pixmap.isNull(): should_hide = True
        if should_hide:
            pixmap_item.setPixmap(QPixmap())
            if self.current_hitbox_item:
                self.current_scene.removeItem(self.current_hitbox_item)
                self.current_hitbox_item = None
            return
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
        
        z_val = int(data.get("z_index", 0))
        if data.get("is_ground"): z_val -= 1000
        pixmap_item.setZValue(z_val)
        
        if self.current_hitbox_item:
            self.current_scene.removeItem(self.current_hitbox_item)
            self.current_hitbox_item = None
        
        if not data.get("is_passable", False):
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

        obj_id = current.data(Qt.UserRole).get("id")
        zone = self.combo_zone_selector.currentText()
        objects = self.current_data.get("zones", {}).get(zone, [])
        data = next((o for o in objects if o.get("id") == obj_id), None)
        if data is None:
            self.disable_property_panel()
            return

        self.enable_property_panel()
        self._block_all_property_signals(True)

        self.prop_id.setText(data.get("id", ""))
        self.prop_type.setCurrentText(data.get("type", "Obstacle"))
        self.prop_x.setValue(data.get("x", 0))
        self.prop_y.setValue(data.get("y", 0))
        self.prop_z_index.setValue(int(data.get("z_index", 0))) 
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
        self.prop_interaction_type.setCurrentText(data.get("interaction_type", "None"))
        itype = data.get("interaction_type", "None")
        idata = data.get("interaction_data", "")
        if itype == "Note": self.data_note_text.setText(str(idata))
        elif itype == "Image": self.data_image_path_combo.setCurrentText(str(idata))
        
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
            
        self._block_all_property_signals(False)

    def on_property_changed(self):
        current_item = self.list_objects.currentItem()
        if not current_item: return
        obj_id = current_item.data(Qt.UserRole).get("id")
        zone = self.combo_zone_selector.currentText()
        objects_list = self.current_data["zones"].get(zone, [])
        data = next((o for o in objects_list if o.get("id") == obj_id), None)
        if data is None: return

        data['type'] = self.prop_type.currentText()
        data['x'] = self.prop_x.value()
        data['y'] = self.prop_y.value()
        data['z_index'] = self.prop_z_index.value() 
        data['image_path'] = self.prop_image_path_combo.currentText()
        data['resize_factor'] = self.prop_resize_factor.value()
        data['is_passable'] = self.prop_is_passable.isChecked()
        data['starts_hidden'] = self.prop_starts_hidden.isChecked()
        data['is_ground'] = self.prop_is_ground.isChecked()
        data['collision_rect_offset'] = [
            self.prop_hitbox_dx.value(), self.prop_hitbox_dy.value(),
            self.prop_hitbox_dw.value(), self.prop_hitbox_dh.value()
        ]
        data['animation_speed'] = self.prop_anim_speed.value()
        anim_images = []
        for i in range(self.prop_anim_list.count()): anim_images.append(self.prop_anim_list.item(i).text())
        data['animation_images'] = anim_images
        data['flash_image_path'] = self.prop_flash_image_path_combo.currentText()
        data['interaction_type'] = self.prop_interaction_type.currentText()
        if data['interaction_type'] == "Note": data['interaction_data'] = self.data_note_text.toPlainText()
        elif data['interaction_type'] == "Image": data['interaction_data'] = self.data_image_path_combo.currentText()
        elif data['interaction_type'] == "Door": data['interaction_data'] = {}
        else: data['interaction_data'] = ""

        current_item.setText(f"[{data['type']}] {data['id']} ")
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if not pixmap_item:
            pixmap_item = self.draw_object_on_canvas(data)
            current_item.setData(Qt.UserRole + 1, pixmap_item)
        if pixmap_item: self.update_canvas_item(data, pixmap_item)

    def add_animation_frame(self):
        start_dir = os.path.join(self.base_path, "assets")
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar", start_dir, "Images (*.png *.jpg)")
        if filepaths:
            for fp in filepaths:
                try: rel = os.path.relpath(fp, self.base_path).replace("\\", "/")
                except: rel = fp
                self.prop_anim_list.addItem(rel)
            self.on_property_changed()

    def remove_animation_frame(self):
        for item in self.prop_anim_list.selectedItems():
            self.prop_anim_list.takeItem(self.prop_anim_list.row(item))
        self.on_property_changed()

    def add_new_object(self):
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key: return
        new_id = f"obj_{int(time.time())}"
        new_obj_data = {
            "id": new_id, "type": "Obstacle", "x": GAME_WIDTH // 2, "y": GAME_HEIGHT // 2, "z_index": 0,
            "image_path": "None", "resize_factor": 1.0, "is_passable": False, "starts_hidden": False, "is_ground": False,
            "collision_rect_offset": [0, 0, 0, 0], "animation_images": [], "animation_speed": 0.1,
            "flash_image_path": "None", "interaction_type": "None", "interaction_data": ""
        }
        if current_zone_key not in self.current_data["zones"]: self.current_data["zones"][current_zone_key] = []
        self.current_data["zones"][current_zone_key].append(new_obj_data)
        item = QListWidgetItem(f"[{new_obj_data['type']}] {new_obj_data['id']}")
        item.setData(Qt.UserRole, new_obj_data)
        self.list_objects.addItem(item)
        self.list_objects.setCurrentItem(item)

    def delete_selected_object(self):
        current_item = self.list_objects.currentItem()
        if not current_item: return
        obj_data = current_item.data(Qt.UserRole)
        zone = self.combo_zone_selector.currentText()
        if zone in self.current_data["zones"]:
            try: self.current_data["zones"][zone].remove(obj_data)
            except: pass
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if pixmap_item:
            if self.current_hitbox_item:
                 self.current_scene.removeItem(self.current_hitbox_item)
                 self.current_hitbox_item = None
            self.current_scene.removeItem(pixmap_item)
        self.list_objects.takeItem(self.list_objects.row(current_item))
        self.disable_property_panel()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())