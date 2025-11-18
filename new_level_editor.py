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
from PySide6.QtCore import Qt, QRectF, QSize

# Importamos la clase que acabamos de compilar
from ui_editor import Ui_LevelEditor 

# --- CONSTANTES GLOBALES ---
GAME_WIDTH = 1280
GAME_HEIGHT = 780
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
# -----------------------------


class LevelEditor(QMainWindow, Ui_LevelEditor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        print(f"Ruta base del proyecto establecida en: {self.base_path}")
        
        self.current_data = {}
        self.image_paths = [] # Lista de todas las imágenes disponibles
        self.current_scene = QGraphicsScene()
        self.canvas_view.setScene(self.current_scene)
        
        self.current_scene.setSceneRect(0, 0, GAME_WIDTH, GAME_HEIGHT)
        self.current_scene.setBackgroundBrush(QBrush(QColor(50, 50, 50)))
        
        self.current_hitbox_item = None
        self.all_image_combos = []

        # --- Conectar Señales (Slots) ---
        self.action_load_json.triggered.connect(self.load_json)
        self.action_save_json.triggered.connect(self.save_json)

        self.btn_add_object.clicked.connect(self.add_new_object)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)

        self.combo_zone_selector.currentIndexChanged.connect(self.populate_views_for_current_zone)
        self.list_objects.currentItemChanged.connect(self.on_object_selected)
        
        # Lógica de UI
        self.prop_interaction_type.currentIndexChanged.connect(self.on_interaction_type_changed)
        self.prop_type.currentIndexChanged.connect(self.on_main_type_changed)

        # Previsualización de Imagen
        self.prop_image_path_combo.currentIndexChanged.connect(self.update_image_preview)
        
        # Botones de Animación
        self.btn_anim_add.clicked.connect(self.add_animation_frame)
        self.btn_anim_remove.clicked.connect(self.remove_animation_frame)
        
        # --- Conectar TODOS los widgets de propiedades a on_property_changed ---
        parent_widget = self.scrollAreaWidgetContents 

        # Tipos con valueChanged (SpinBox para números)
        for widget in parent_widget.findChildren(QSpinBox):
            widget.valueChanged.connect(self.on_property_changed)
        for widget in parent_widget.findChildren(QDoubleSpinBox):
            widget.valueChanged.connect(self.on_property_changed)
            
        # Tipos con editingFinished (Campos de texto de una línea)
        for widget in parent_widget.findChildren(QLineEdit):
            widget.editingFinished.connect(self.on_property_changed)
            
        # Tipos con stateChanged (Checkboxes)
        for widget in parent_widget.findChildren(QCheckBox):
            widget.stateChanged.connect(self.on_property_changed) # Usa stateChanged
            
        # Tipos con textChanged (Campos de texto multi-línea)
        for widget in parent_widget.findChildren(QTextEdit):
            widget.textChanged.connect(self.on_property_changed)
            
        # Tipos con currentIndexChanged (Listas desplegables)
        # Conectamos manualmente los que no se conectaron ya
        self.prop_type.currentIndexChanged.connect(self.on_property_changed)
        self.prop_interaction_type.currentIndexChanged.connect(self.on_property_changed)
        self.prop_image_path_combo.currentIndexChanged.connect(self.on_property_changed)
        self.prop_flash_image_path_combo.currentIndexChanged.connect(self.on_property_changed)
        self.data_image_path_combo.currentIndexChanged.connect(self.on_property_changed)
        
        self.prop_anim_list.itemChanged.connect(self.on_property_changed)
        # --- FIN DEL BLOQUE ---


        # Inicializar la vista
        self.all_image_combos = [
            self.prop_image_path_combo, 
            self.prop_flash_image_path_combo, 
            self.data_image_path_combo
        ]
        self.populate_image_combos() 
        self.on_interaction_type_changed(0)
        self.disable_property_panel()
        print("Editor inicializado.")

    # --- Funciones de Lógica de UI ---

    def disable_property_panel(self):
        self.properties_box.setEnabled(False)
        self.group_interaction.setEnabled(False)
        self.group_animation.setEnabled(False)

    def enable_property_panel(self):
        self.properties_box.setEnabled(True)
        self.group_animation.setEnabled(True)
        self.on_main_type_changed() # Esto manejará si group_interaction se activa

    def on_main_type_changed(self):
        is_interactable = self.prop_type.currentText() == "Interactable"
        self.group_interaction.setEnabled(is_interactable)
        
        if not is_interactable:
            # Forzar a "None" si el objeto no es interactuable
            self.prop_interaction_type.blockSignals(True)
            self.prop_interaction_type.setCurrentIndex(0) # 0 es "None"
            self.prop_interaction_type.blockSignals(False)
            
        # self.on_property_changed() # No llamar aquí, ya está conectado
        
    def on_interaction_type_changed(self, index):
        combo_text = self.prop_interaction_type.currentText()
        
        if combo_text == "Note":
            self.prop_interaction_data_stack.setCurrentIndex(0) 
            self.stack_page_note.setEnabled(True)
        elif combo_text == "Image":
            self.prop_interaction_data_stack.setCurrentIndex(1)
        elif combo_text == "Door":
            self.prop_interaction_data_stack.setCurrentIndex(2) 
        else: # "None"
            self.prop_interaction_data_stack.setCurrentIndex(0)
            self.stack_page_note.setEnabled(False)

    def populate_image_combos(self):
        """Escanea assets/images y assets/animations y llena los QComboBox."""
        self.image_paths = ["None"] 
        
        scan_folders = ["assets/images", "assets/animations"]
        for folder in scan_folders:
            folder_path = os.path.join(self.base_path, folder)
            if not os.path.exists(folder_path):
                print(f"Advertencia: La carpeta no existe: {folder_path}")
                continue
                
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(IMAGE_EXTENSIONS):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, self.base_path)
                        self.image_paths.append(relative_path.replace("\\", "/"))
        
        for combo in self.all_image_combos:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(self.image_paths)
            combo.blockSignals(False)
            
    def update_image_preview(self):
        """Muestra la imagen principal en el QLabel de previsualización."""
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

    # --- Funciones de Carga/Guardado de Datos ---

    def load_json(self):
        """Carga un archivo JSON (formato nuevo) y puebla el selector de zonas."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Cargar JSON", self.base_path, "JSON Files (*.json)")
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                self.current_data = json.load(f)
            
            self.combo_zone_selector.blockSignals(True)
            self.combo_zone_selector.clear()
            zone_keys = list(self.current_data.get("zones", {}).keys())
            self.combo_zone_selector.addItems(zone_keys)
            self.combo_zone_selector.blockSignals(False)
            
            if zone_keys:
                self.populate_views_for_current_zone()
            
            self.statusbar.showMessage(f"Se cargó: {filepath}", 5000)
            
        except Exception as e:
            print(f"Error al cargar JSON: {e}")
            self.statusbar.showMessage(f"Error al cargar: {e}", 5000)

    def populate_views_for_current_zone(self):
        """Limpia y puebla la lista y el lienzo basado en la zona."""
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key:
            return

        objects_list = self.current_data.get("zones", {}).get(current_zone_key, [])
        
        self.list_objects.blockSignals(True)
        self.list_objects.clear()
        self.current_scene.clear()
        self.current_hitbox_item = None
        self.disable_property_panel()
        
        for i, obj_data in enumerate(objects_list):
            if "id" not in obj_data:
                obj_data["id"] = f"{current_zone_key}_obj_{i}"

            item_text = f"[{obj_data.get('type', 'Obj')}] {obj_data['id']}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, obj_data)
            self.list_objects.addItem(list_item)
            
            pixmap_item = self.draw_object_on_canvas(obj_data)
            if pixmap_item:
                list_item.setData(Qt.UserRole + 1, pixmap_item)

        self.list_objects.blockSignals(False)
        
        self.current_hitbox_item = self.current_scene.addRect(0, 0, 0, 0, QPen(QColor(255, 0, 0, 200), 2, Qt.DashLine))
        self.current_hitbox_item.setVisible(False)

    def draw_object_on_canvas(self, obj_data):
        """Helper para dibujar un solo objeto en el lienzo."""
        image_path = obj_data.get('image_path')
        if not image_path or image_path == "None": return None
        
        absolute_image_path = os.path.join(self.base_path, image_path)
        pixmap = QPixmap(absolute_image_path)
        if pixmap.isNull():
            print(f"Advertencia: No se pudo cargar la imagen {absolute_image_path}")
            return None
            
        resize_factor = obj_data.get('resize_factor', 4) 
        width = pixmap.width() * resize_factor
        height = pixmap.height() * resize_factor
        
        if width <= 0 or height <= 0:
            return None
            
        scaled_pixmap = pixmap.scaled(int(width), int(height), Qt.KeepAspectRatio)
        pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
        
        x = obj_data.get('x', 0)
        y = obj_data.get('y', 0)
        pixmap_item.setPos(x - (width / 2), y - (height / 2))
        
        self.current_scene.addItem(pixmap_item)
        return pixmap_item

    def on_object_selected(self, current_item, previous_item):
        """Puebla el panel de propiedades cuando se selecciona un item."""
        if not current_item:
            self.disable_property_panel()
            if self.current_hitbox_item:
                self.current_hitbox_item.setVisible(False)
            return

        self.enable_property_panel()
        obj_data = current_item.data(Qt.UserRole)
        
        self._block_all_property_signals(True)

        self.prop_id.setText(obj_data.get('id', 'N/A'))
        self.prop_type.setCurrentText(obj_data.get('type', 'Obstacle'))
        self.prop_x.setValue(obj_data.get('x', 0))
        self.prop_y.setValue(obj_data.get('y', 0))
        self.prop_image_path_combo.setCurrentText(obj_data.get('image_path', 'None'))
        self.update_image_preview() 
        self.prop_resize_factor.setValue(obj_data.get('resize_factor', 4.0))
        self.prop_is_passable.setChecked(obj_data.get('is_passable', False))
        self.prop_starts_hidden.setChecked(obj_data.get('starts_hidden', False))
        
        hitbox = obj_data.get('collision_rect_offset', [0, 0, 0, 0])
        self.prop_hitbox_dx.setValue(hitbox[0])
        self.prop_hitbox_dy.setValue(hitbox[1])
        self.prop_hitbox_dw.setValue(hitbox[2])
        self.prop_hitbox_dh.setValue(hitbox[3])
        
        # Animación
        self.prop_anim_list.clear()
        self.prop_anim_list.addItems(obj_data.get('animation_images', []))
        self.prop_anim_speed.setValue(obj_data.get('animation_speed', 0.1))
        
        # Interacción
        self.prop_flash_image_path_combo.setCurrentText(obj_data.get('flash_image_path', 'None'))
        interaction_type = obj_data.get('interaction_type', 'None')
        index = self.prop_interaction_type.findText(interaction_type)
        if index != -1: self.prop_interaction_type.setCurrentIndex(index)
        
        interaction_data = obj_data.get('interaction_data')
        if interaction_type == "Note":
            self.data_note_text.setText("\n".join(interaction_data or []))
        elif interaction_type == "Image":
            self.data_image_path_combo.setCurrentText(interaction_data or "None")
        
        self.on_main_type_changed()
        self.update_canvas_item(obj_data, current_item.data(Qt.UserRole + 1))
        
        self._block_all_property_signals(False)
        
    def _block_all_property_signals(self, block: bool):
        """Helper para bloquear/desbloquear señales de todos los widgets de propiedades."""
        parent_widget = self.scrollAreaWidgetContents
        types_to_block = (QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit, QListWidget)
        
        for widget_type in types_to_block:
            for widget in parent_widget.findChildren(widget_type):
                widget.blockSignals(block)

    # --- Funciones de Edición ---

    def on_property_changed(self):
        """
        ¡Función clave! Se llama cada vez que se edita una propiedad.
        Actualiza self.current_data EN TIEMPO REAL.
        """
        current_item = self.list_objects.currentItem()
        if not current_item:
            return

        obj_data = current_item.data(Qt.UserRole)
        
        # 1. Leer TODOS los datos desde la UI y guardarlos en el dict
        obj_data['type'] = self.prop_type.currentText()
        obj_data['x'] = self.prop_x.value()
        obj_data['y'] = self.prop_y.value()
        obj_data['image_path'] = self.prop_image_path_combo.currentText()
        obj_data['resize_factor'] = self.prop_resize_factor.value()
        obj_data['is_passable'] = self.prop_is_passable.isChecked()
        obj_data['starts_hidden'] = self.prop_starts_hidden.isChecked()
        
        obj_data['collision_rect_offset'] = [
            self.prop_hitbox_dx.value(),
            self.prop_hitbox_dy.value(),
            self.prop_hitbox_dw.value(),
            self.prop_hitbox_dh.value()
        ]
        
        # Animación
        obj_data['animation_speed'] = self.prop_anim_speed.value()
        anim_images = []
        for i in range(self.prop_anim_list.count()):
            anim_images.append(self.prop_anim_list.item(i).text())
        obj_data['animation_images'] = anim_images
        
        # Interacción
        obj_data['flash_image_path'] = self.prop_flash_image_path_combo.currentText()
        obj_data['interaction_type'] = self.prop_interaction_type.currentText()
        
        if obj_data['interaction_type'] == "Note":
            obj_data['interaction_data'] = self.data_note_text.toPlainText().split('\n')
        elif obj_data['interaction_type'] == "Image":
            obj_data['interaction_data'] = self.data_image_path_combo.currentText()
        elif obj_data['interaction_type'] == "Door":
            obj_data['interaction_data'] = {} # TODO
        else: # "None"
            obj_data['interaction_data'] = None

        # 2. Actualizar la lista (el texto)
        item_text = f"[{obj_data['type']}] {obj_data['id']}"
        current_item.setText(item_text)

        # 3. Actualizar el lienzo (la imagen y el hitbox)
        pixmap_item = current_item.data(Qt.UserRole + 1)
        self.update_canvas_item(obj_data, pixmap_item)

    def update_canvas_item(self, obj_data, pixmap_item):
        """Actualiza la posición, imagen y hitbox de un item en el lienzo."""
        if not pixmap_item:
            pixmap_item = self.draw_object_on_canvas(obj_data)
            if pixmap_item and self.list_objects.currentItem():
                self.list_objects.currentItem().setData(Qt.UserRole + 1, pixmap_item)
            else:
                return 
        
        image_path = obj_data.get('image_path')
        if not image_path or image_path == "None":
            pixmap_item.setPixmap(QPixmap()) 
            self.current_hitbox_item.setVisible(False)
            return
            
        absolute_image_path = os.path.join(self.base_path, image_path)
        pixmap = QPixmap(absolute_image_path)
        
        if pixmap.isNull():
            pixmap_item.setPixmap(QPixmap())
            self.current_hitbox_item.setVisible(False)
            return

        resize_factor = obj_data.get('resize_factor', 4)
        width = pixmap.width() * resize_factor
        height = pixmap.height() * resize_factor
        
        if width <= 0 or height <= 0:
            return

        scaled_pixmap = pixmap.scaled(int(width), int(height), Qt.KeepAspectRatio)
        pixmap_item.setPixmap(scaled_pixmap)
        
        x = obj_data.get('x', 0)
        y = obj_data.get('y', 0)
        pixmap_item.setPos(x - (width / 2), y - (height / 2))
        
        offset = obj_data.get('collision_rect_offset', [0, 0, 0, 0])
        sprite_top_left_x = x - (width / 2)
        sprite_top_left_y = y - (height / 2)
        
        hitbox_x = sprite_top_left_x + offset[0]
        hitbox_y = sprite_top_left_y + offset[1]
        hitbox_w = width + offset[2]
        hitbox_h = height + offset[3]
        
        self.current_hitbox_item.setRect(hitbox_x, hitbox_y, hitbox_w, hitbox_h)
        self.current_hitbox_item.setVisible(not obj_data.get('is_passable', False))

    def add_animation_frame(self):
        """Añade un frame a la lista de animación."""
        start_dir = os.path.join(self.base_path, "assets") 
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar Frame de Animación", start_dir, "Image Files (*.png *.jpg)")
        if filepath:
            try:
                relative_path = os.path.relpath(filepath, self.base_path)
                self.prop_anim_list.addItem(relative_path.replace("\\", "/"))
                self.on_property_changed() # Guardar el cambio
            except ValueError:
                self.prop_anim_list.addItem(filepath.replace("\\", "/"))
                self.on_property_changed()

    def remove_animation_frame(self):
        """Quita el frame seleccionado de la lista de animación."""
        current_item = self.prop_anim_list.currentItem()
        if current_item:
            self.prop_anim_list.takeItem(self.prop_anim_list.row(current_item))
            self.on_property_changed() # Guardar el cambio

    def add_new_object(self):
        """
        Añade un objeto nuevo por defecto a la zona actual.
        MODIFICADO: Ahora añade un objeto "en blanco" (None)
        """
        current_zone_key = self.combo_zone_selector.currentText()
        if not current_zone_key:
            return

        new_id = f"obj_{int(time.time())}" 
        new_obj_data = {
            "id": new_id,
            "type": "Obstacle", 
            "x": GAME_WIDTH // 2, 
            "y": GAME_HEIGHT // 2,
            "image_path": "None", # <-- MODIFICADO: Empezar en blanco
            "resize_factor": 1,
            "is_passable": False,
            "starts_hidden": False,
            "collision_rect_offset": [0, 0, 0, 0],
            "animation_images": [],
            "animation_speed": 0.1,
            "flash_image_path": "None",
            "interaction_type": "None",
            "interaction_data": None
        }
        
        # Añadir a los datos en memoria
        if current_zone_key not in self.current_data["zones"]:
            self.current_data["zones"][current_zone_key] = []
        self.current_data["zones"][current_zone_key].append(new_obj_data)
        
        # Añadir a la lista
        item_text = f"[{new_obj_data['type']}] {new_obj_data['id']}"
        list_item = QListWidgetItem(item_text)
        
        # --- ¡¡¡ESTA ES LA LÍNEA CORREGIDA!!! ---
        list_item.setData(Qt.UserRole, new_obj_data) # <-- Debe ser new_obj_data
        # ----------------------------------------
        
        self.list_objects.addItem(list_item)
        
        # Añadir al lienzo (no dibujará nada, pero necesitamos el item)
        pixmap_item = self.draw_object_on_canvas(new_obj_data)
        if pixmap_item:
            list_item.setData(Qt.UserRole + 1, pixmap_item)
            
        self.list_objects.setCurrentItem(list_item)
        self.statusbar.showMessage(f"Objeto {new_id} añadido. ¡Configúralo!", 3000)

    def delete_selected_object(self):
        """Elimina el objeto seleccionado de la lista, el lienzo y los datos."""
        current_item = self.list_objects.currentItem()
        if not current_item:
            return

        obj_data = current_item.data(Qt.UserRole)
        pixmap_item = current_item.data(Qt.UserRole + 1)
        current_zone_key = self.combo_zone_selector.currentText()

        try:
            self.current_data["zones"][current_zone_key].remove(obj_data)
            
            if pixmap_item:
                self.current_scene.removeItem(pixmap_item)
                
            self.list_objects.takeItem(self.list_objects.row(current_item))
            
            self.statusbar.showMessage(f"Objeto {obj_data['id']} eliminado.", 3000)
            self.disable_property_panel()
            
        except Exception as e:
            print(f"Error al eliminar: {e}")
            self.statusbar.showMessage(f"Error al eliminar: {e}", 5000)

    def save_json(self):
        """
        Guarda el self.current_data (que ahora está actualizado en tiempo real)
        en un archivo JSON.
        """
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", self.base_path, "JSON Files (*.json)")
        if not filepath:
            return
            
        try:
            with open(filepath, 'w') as f:
                json.dump(self.current_data, f, indent=4)
            self.statusbar.showMessage(f"Se guardó en: {filepath}", 5000)
        except Exception as e:
            self.statusbar.showMessage(f"Error al guardar: {e}", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())