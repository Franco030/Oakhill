import sys
import json
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QGraphicsScene, QGraphicsPixmapItem,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QListWidget
)
from PySide6.QtGui import QPixmap, QBrush, QColor, QPen
from PySide6.QtCore import Qt
from ui_editor import Ui_LevelEditor

GAME_WIDTH = 1280
GAME_HEIGHT = 780
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


class LevelEditor(QMainWindow, Ui_LevelEditor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.current_data = {"zones": {}}
        self.image_paths = []

        self.current_scene = QGraphicsScene()
        self.canvas_view.setScene(self.current_scene)
        self.current_scene.setSceneRect(0, 0, GAME_WIDTH, GAME_HEIGHT)
        self.current_scene.setBackgroundBrush(QBrush(QColor(50, 50, 50)))

        self.current_hitbox_item = None

        self.all_image_combos = [
            self.prop_image_path_combo,
            self.prop_flash_image_path_combo,
            self.data_image_path_combo
        ]

        self.action_load_json.triggered.connect(self.load_json)
        self.action_save_json.triggered.connect(self.save_json)
        self.btn_add_object.clicked.connect(self.add_new_object)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)
        self.combo_zone_selector.currentIndexChanged.connect(self.populate_views_for_current_zone)
        self.list_objects.currentItemChanged.connect(self.on_object_selected)

        self.prop_x.valueChanged.connect(self.on_property_changed)
        self.prop_y.valueChanged.connect(self.on_property_changed)
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

        self.data_note_text.textChanged.connect(self.on_property_changed)

        self.btn_anim_add.clicked.connect(self.add_animation_frame)
        self.btn_anim_remove.clicked.connect(self.remove_animation_frame)

        self.prop_image_path_combo.currentTextChanged.connect(self.update_image_preview)
        self.prop_type.currentTextChanged.connect(self.on_main_type_changed)
        self.prop_interaction_type.currentTextChanged.connect(self.on_interaction_type_changed)

        self.populate_image_combos()
        self.disable_property_panel()

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
            self.current_hitbox_item.setVisible(False)

    def enable_property_panel(self):
        self.properties_box.setEnabled(True)
        self.on_main_type_changed()

    def on_main_type_changed(self):
        is_interactable = self.prop_type.currentText() == "Interactable"
        self.group_interaction.setEnabled(is_interactable)
        self.group_animation.setEnabled(True)

    def on_interaction_type_changed(self):
        combo_text = self.prop_interaction_type.currentText()
        
        if combo_text == "Note":
            self.prop_interaction_data_stack.setCurrentIndex(0)
        elif combo_text == "Image":
            self.prop_interaction_data_stack.setCurrentIndex(1)
        elif combo_text == "Door":
            self.prop_interaction_data_stack.setCurrentIndex(2)
        else:
            self.prop_interaction_data_stack.setCurrentIndex(0)

    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Cargar JSON", self.base_path, "JSON (*.json)")
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
        except Exception as e:
            print(f"Error al cargar JSON: {e}")
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
                    if obj.get(k) in (None, "None"):
                        obj[k] = ""
                try:
                    obj["resize_factor"] = float(obj.get("resize_factor", 1))
                except:
                    obj["resize_factor"] = 1.0
                
                itype = obj.get("interaction_type", "None")
                if itype == "Note":
                    d = obj.get("interaction_data")
                    if isinstance(d, list):
                        obj["interaction_data"] = "\n".join(d)
                    elif d is None:
                        obj["interaction_data"] = ""
                    else:
                        obj["interaction_data"] = str(d)
                elif itype == "Image":
                    d = obj.get("interaction_data")
                    obj["interaction_data"] = "" if d in (None, "None") else str(d)
                elif itype == "Door":
                    if obj.get("interaction_data") is None:
                        obj["interaction_data"] = {}
                else:
                    obj["interaction_data"] = ""

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", self.base_path, "JSON (*.json)")
        if not filepath:
            return

        try:
            self.sanitize_before_save()
        except Exception as e:
            print(f"Error en sanitize_before_save: {e}")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.current_data, f, indent=4, ensure_ascii=False)
            print("JSON guardado en:", filepath)
        except Exception as e:
            print(f"Error al guardar JSON: {e}")

    def populate_image_combos(self):
        self.image_paths = ["None"]

        for folder in ["assets/images", "assets/animations"]:
            full = os.path.join(self.base_path, folder)
            if not os.path.exists(full):
                continue
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
        if not zone or "zones" not in self.current_data:
            return
            
        if zone not in self.current_data["zones"]:
             self.current_data["zones"][zone] = []

        for obj in self.current_data["zones"].get(zone, []):
            item_text = f"[{obj.get('type','Obj')}] {obj.get('id','NO_ID')} "
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, obj)
            self.list_objects.addItem(item)
            pix = self.draw_object_on_canvas(obj)
            if pix:
                item.setData(Qt.UserRole + 1, pix)

        self.current_hitbox_item = self.current_scene.addRect(0, 0, 0, 0, QPen(QColor(255, 0, 0), 2, Qt.DashLine))
        self.current_hitbox_item.setVisible(False)

    def draw_object_on_canvas(self, obj):
        imgpath = obj.get("image_path", "None")
        if imgpath in (None, "None", ""):
            return None

        full = os.path.join(self.base_path, imgpath)
        if not os.path.exists(full):
            print(f"Advertencia: No se encuentra la imagen {imgpath}")
            return None

        pixmap = QPixmap(full)
        if pixmap.isNull():
            return None

        try:
            factor = float(obj.get("resize_factor", 1))
            if factor <= 0: factor = 1
        except:
            factor = 1
            
        scaled = pixmap.scaled(
            int(pixmap.width() * factor),
            int(pixmap.height() * factor),
            Qt.KeepAspectRatio
        )

        item = QGraphicsPixmapItem(scaled)
        item.setPos(obj.get("x", 0) - scaled.width() / 2,
                     obj.get("y", 0) - scaled.height() / 2)
        self.current_scene.addItem(item)
        return item

    def update_canvas_item(self, data, pixmap_item):
        if not pixmap_item:
            return

        imgpath = data.get("image_path", "None")
        if imgpath in (None, "None", ""):
            pixmap_item.setPixmap(QPixmap())
            self.current_hitbox_item.setVisible(False)
            return

        full = os.path.join(self.base_path, imgpath)
        if not os.path.exists(full):
            pixmap_item.setPixmap(QPixmap())
            self.current_hitbox_item.setVisible(False)
            return
            
        pixmap = QPixmap(full)
        if pixmap.isNull():
            pixmap_item.setPixmap(QPixmap())
            self.current_hitbox_item.setVisible(False)
            return

        try:
            factor = float(data.get("resize_factor", 1))
            if factor <= 0: factor = 1
        except:
            factor = 1

        scaled = pixmap.scaled(
            int(pixmap.width() * factor),
            int(pixmap.height() * factor),
            Qt.KeepAspectRatio
        )
        
        pixmap_item.setPixmap(scaled)
        
        x = data.get("x", 0)
        y = data.get("y", 0)
        width = scaled.width()
        height = scaled.height()
        
        pixmap_item.setPos(x - (width / 2), y - (height / 2))
        
        offset = data.get("collision_rect_offset", [0, 0, 0, 0])
        sprite_top_left_x = x - (width / 2)
        sprite_top_left_y = y - (height / 2)
        
        hitbox_x = sprite_top_left_x + offset[0]
        hitbox_y = sprite_top_left_y + offset[1]
        hitbox_w = width + offset[2]
        hitbox_h = height + offset[3]
        
        self.current_hitbox_item.setRect(hitbox_x, hitbox_y, hitbox_w, hitbox_h)
        self.current_hitbox_item.setVisible(not data.get("is_passable", False))

    def update_image_preview(self):
        path = self.prop_image_path_combo.currentText()
        if not path or path == "None":
            self.prop_image_preview.clear()
            self.prop_image_preview.setText("None")
            return

        full_path = os.path.join(self.base_path, path)
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            self.prop_image_preview.setText("Error")
        else:
            scaled_pixmap = pixmap.scaled(self.prop_image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.prop_image_preview.setPixmap(scaled_pixmap)

    def on_object_selected(self, current, previous):
        if not current:
            self.disable_property_panel()
            return

        obj_id = current.data(Qt.UserRole).get("id")
        zone = self.combo_zone_selector.currentText()
        objects = self.current_data.get("zones", {}).get(zone, [])
        data = next((o for o in objects if o.get("id") == obj_id), None)
        
        if data is None:
            print(f"SYNC ERROR: objeto {obj_id} no encontrado en on_object_selected")
            self.disable_property_panel()
            return

        self.enable_property_panel()
        
        self._block_all_property_signals(True)

        self.prop_id.setText(data.get("id", ""))
        self.prop_type.setCurrentText(data.get("type", "Obstacle"))
        self.prop_x.setValue(data.get("x", 0))
        self.prop_y.setValue(data.get("y", 0))
        self.prop_image_path_combo.setCurrentText(data.get("image_path", "None"))
        
        try:
            resize_val = float(data.get("resize_factor", 1))
        except:
            resize_val = 1.0
        self.prop_resize_factor.setValue(resize_val)
        
        self.prop_is_passable.setChecked(data.get("is_passable", False))
        self.prop_starts_hidden.setChecked(data.get("starts_hidden", False))

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
        
        if itype == "Note":
            self.data_note_text.setText(str(idata))
        elif itype == "Image":
            self.data_image_path_combo.setCurrentText(str(idata))
        
        self.update_image_preview()
        
        pixmap_item = current.data(Qt.UserRole + 1)
        if pixmap_item:
            self.update_canvas_item(data, pixmap_item)
        else:
            new_pixmap_item = self.draw_object_on_canvas(data)
            if new_pixmap_item:
                current.setData(Qt.UserRole + 1, new_pixmap_item)
                self.update_canvas_item(data, new_pixmap_item)
            
        self._block_all_property_signals(False)

    def on_property_changed(self):
        current_item = self.list_objects.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole).get("id")
        zone = self.combo_zone_selector.currentText()
        
        if not zone or not obj_id:
            return
            
        objects_list = self.current_data["zones"].get(zone, [])
        data = next((o for o in objects_list if o.get("id") == obj_id), None)

        if data is None:
            print(f"SYNC ERROR: objeto {obj_id} no encontrado en on_property_changed")
            return

        data['type'] = self.prop_type.currentText()
        data['x'] = self.prop_x.value()
        data['y'] = self.prop_y.value()
        data['image_path'] = self.prop_image_path_combo.currentText()
        data['resize_factor'] = self.prop_resize_factor.value()
        data['is_passable'] = self.prop_is_passable.isChecked()
        data['starts_hidden'] = self.prop_starts_hidden.isChecked()
        
        data['collision_rect_offset'] = [
            self.prop_hitbox_dx.value(),
            self.prop_hitbox_dy.value(),
            self.prop_hitbox_dw.value(),
            self.prop_hitbox_dh.value()
        ]
        
        data['animation_speed'] = self.prop_anim_speed.value()
        anim_images = []
        for i in range(self.prop_anim_list.count()):
            anim_images.append(self.prop_anim_list.item(i).text())
        data['animation_images'] = anim_images
        
        data['flash_image_path'] = self.prop_flash_image_path_combo.currentText()
        data['interaction_type'] = self.prop_interaction_type.currentText()
        
        if data['interaction_type'] == "Note":
            data['interaction_data'] = self.data_note_text.toPlainText()
        elif data['interaction_type'] == "Image":
            data['interaction_data'] = self.data_image_path_combo.currentText()
        elif data['interaction_type'] == "Door":
            data['interaction_data'] = {}
        else:
            data['interaction_data'] = ""

        current_item.setText(f"[{data['type']}] {data['id']} ")
        
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if not pixmap_item:
            pixmap_item = self.draw_object_on_canvas(data)
            current_item.setData(Qt.UserRole + 1, pixmap_item)
        
        if pixmap_item:
            self.update_canvas_item(data, pixmap_item)

    def add_animation_frame(self):
        start_dir = os.path.join(self.base_path, "assets")
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Frames de Animación", start_dir, "Image Files (*.png *.jpg)")
        
        if filepaths:
            paths_to_add = []
            for filepath in filepaths:
                try:
                    relative_path = os.path.relpath(filepath, self.base_path)
                    paths_to_add.append(relative_path.replace("\\", "/"))
                except ValueError:
                    paths_to_add.append(filepath.replace("\\", "/"))
            
            self.prop_anim_list.addItems(paths_to_add)
            self.on_property_changed()

    def remove_animation_frame(self):
        selected_items = self.prop_anim_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.prop_anim_list.takeItem(self.prop_anim_list.row(item))
        self.on_property_changed()

    def add_new_object(self):
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key:
            return

        new_id = f"obj_{int(time.time())}"
        new_obj_data = {
            "id": new_id,
            "type": "Obstacle",
            "x": GAME_WIDTH // 2,
            "y": GAME_HEIGHT // 2,
            "image_path": "None",
            "resize_factor": 1.0,
            "is_passable": False,
            "starts_hidden": False,
            "collision_rect_offset": [0, 0, 0, 0],
            "animation_images": [],
            "animation_speed": 0.1,
            "flash_image_path": "None",
            "interaction_type": "None",
            "interaction_data": ""
        }

        if current_zone_key not in self.current_data["zones"]:
            self.current_data["zones"][current_zone_key] = []
        self.current_data["zones"][current_zone_key].append(new_obj_data)

        item_text = f"[{new_obj_data['type']}] {new_obj_data['id']}"
        list_item = QListWidgetItem(item_text)
        list_item.setData(Qt.UserRole, new_obj_data)
        self.list_objects.addItem(list_item)
        
        self.list_objects.setCurrentItem(list_item)

    def delete_selected_object(self):
        current_item = self.list_objects.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole).get("id")
        zone = self.combo_zone_selector.currentText()
        
        if not zone or not obj_id:
            return

        objects_list = self.current_data["zones"].get(zone, [])
        obj_to_remove = next((o for o in objects_list if o.get("id") == obj_id), None)
        
        if obj_to_remove:
            try:
                objects_list.remove(obj_to_remove)
            except ValueError:
                print(f"SYNC ERROR: No se pudo eliminar {obj_id} de self.current_data")
        else:
            print(f"SYNC ERROR: No se pudo encontrar {obj_id} en self.current_data para eliminar.")
            
        pixmap_item = current_item.data(Qt.UserRole + 1)
        if pixmap_item:
            self.current_scene.removeItem(pixmap_item)

        self.list_objects.takeItem(self.list_objects.row(current_item))
        
        self.disable_property_panel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())