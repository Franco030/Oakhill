import copy
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
from .EditorCommands import CmdTransform
from src.Game_Constants import MAPS

class ResizeHandle(QGraphicsRectItem):
    """
    A visual handle (blue square) attached to 'Primitive' objects in the editor.
    It intercepts mouse events to allow the user to resize the parent object by dragging.
    """
    def __init__(self, parent_hitbox, editor_ref):
        """
        Description: Initializes the resize handle.
        Parameters:
            parent_item (LevelObjectItem): The visual object this handle controls.
            editor_ref (LevelEditor): Reference to the main editor to trigger UI updates and commands.
        Functionality:
            - Creates a 10x10 blue rectangle.
            - Sets flags to make it movable and selectable.
            - Sets Z-Value high to ensure it renders on top of other items.
        """
        super().__init__(0, 0, 10, 10, parent_hitbox)
        self.parent_hitbox = parent_hitbox
        self.editor = editor_ref
        self.setBrush(QBrush(QColor(0, 0, 255, 200)))
        self.setPen(QPen(Qt.NoPen))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsSelectable)
        self.update_position_from_parent()
    def update_position_from_parent(self):
        """
        Description: Repositions the handle to the bottom-right corner of the parent item.
        Functionality:
            - Gets the bounding rect of the parent's pixmap.
            - Updates self position to (width - 5, height - 5).
        """
        rect = self.parent_hitbox.rect()
        self.setPos(rect.width() - 5, rect.height() - 5)
    def mousePressEvent(self, event):
        """
        Description: Handles the start of a drag operation.
        Functionality:
            - Records the initial width and height of the parent object to support Undo.
            - Passes the event to the base class to handle movement logic.
        """
        data = self.parent_hitbox.obj_data
        self.start_offset = copy.deepcopy(data.get('collision_rect_offset', [0,0,0,0]))
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        """
        Description: Handles the end of a drag operation.
        Functionality:
            - Compares the final size with the start size.
            - If changes occurred, triggers a UI refresh to sync the property panel.
            - (Note: The CmdTransform is implicitly handled during itemChange or manual updates via logic).
        """
        super().mouseReleaseEvent(event)
        data = self.parent_hitbox.obj_data
        end_offset = data.get('collision_rect_offset', [0,0,0,0])
        if self.start_offset != end_offset and self.editor:
            cmd = CmdTransform(self.editor, data, (data['x'], data['y']), (data['x'], data['y']), self.start_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        """
        Description: Reacts to item state changes, specifically position changes during dragging.
        Functionality:
            - Calculates the new width/height based on the mouse/handle position relative to the parent.
            - Enforces a minimum size (10x10).
            - Updates the parent object's data dictionary directly.
            - Calls 'update_canvas_from_resize' on the editor to regenerate the visual primitive in real-time.
        """
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if self.parent_hitbox.ignore_movement: return super().itemChange(change, value)
            new_pos = value
            new_width = max(1, int(new_pos.x() + 5))
            new_height = max(1, int(new_pos.y() + 5))
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
    """
    Visual representation of the collision hitbox (red rectangle).
    Allows the user to drag the hitbox independently of the sprite to adjust the offset.
    """
    def __init__(self, rect, obj_data, parent_sprite_item, editor_ref):
        """
        Description: Initializes the hitbox item.
        Parameters:
            rect (QRectF): The initial geometry of the hitbox.
            obj_data (dict): Reference to the object data.
            parent_sprite_item (LevelObjectItem): The parent visual object.
        """
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
        """
        Description: Records the initial hitbox offset before dragging starts.
        """
        self.start_pos_offset = copy.deepcopy(self.obj_data.get('collision_rect_offset', [0,0,0,0]))
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        """
        Description: Finalizes the drag operation.
        Functionality:
            - Compares start and end offsets.
            - Pushes a CmdTransform to the UndoManager if the offset changed.
        """
        super().mouseReleaseEvent(event)
        end_offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
        if self.start_pos_offset != end_offset and self.editor:
            cmd = CmdTransform(self.editor, self.obj_data, (self.obj_data['x'], self.obj_data['y']), (self.obj_data['x'], self.obj_data['y']), self.start_pos_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        """
        Description: Handles position changes.
        Functionality:
            - Calculates the new offset relative to the parent sprite.
            - Updates the 'collision_rect_offset' in the data dictionary.
            - Syncs the UI SpinBoxes in the editor via 'sync_hitbox_pos_ui'.
            - Ignores updates if 'ignore_movement' is True (to prevent feedback loops).
        """
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
    """
    The main visual representation of a game object (Sprite or Primitive) on the canvas.
    Handles selection, movement, and grid snapping.
    """
    def __init__(self, pixmap, obj_data, editor_ref):
        """
        Description: Initializes the object item.
        Parameters:
            pixmap (QPixmap): The image or generated graphic to display.
            obj_data (dict): Reference to the object's data dictionary.
            editor_ref (LevelEditor): Reference to the editor controller.
        """
        super().__init__(pixmap)
        self.obj_data = obj_data
        self.editor = editor_ref
        self.ignore_movement = False
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.resize_handle = None
    def mousePressEvent(self, event):
        """
        Description: Records initial position before dragging.
        """
        self.start_x = self.obj_data.get('x', 0)
        self.start_y = self.obj_data.get('y', 0)
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        """
        Description: Finalizes drag operation.
        Functionality:
            - Compares start and end positions.
            - Pushes a CmdTransform to UndoManager if position changed.
        """
        super().mouseReleaseEvent(event)
        end_x = self.obj_data.get('x', 0)
        end_y = self.obj_data.get('y', 0)
        if (self.start_x != end_x or self.start_y != end_y) and self.editor:
            offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
            cmd = CmdTransform(self.editor, self.obj_data, (self.start_x, self.start_y), (end_x, end_y), offset, offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
    def itemChange(self, change, value):
        """
        Description: Handles real-time movement logic.
        Functionality:
            - Checks for Grid Snapping if enabled in the editor.
            - Rounds coordinates to the nearest grid cell multiple.
            - Updates the 'x' and 'y' in the data dictionary.
            - Syncs the UI SpinBoxes.
            - Updates the position of the ResizeHandle if it exists.
        """
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
    def create_primitive_handle(self):
        """
        Description: Creates a ResizeHandle if the object is a Primitive and doesn't have one.
        """
        if self.obj_data.get("type") == "Primitive" and not self.resize_handle:
            self.resize_handle = PrimitiveHandle(self, self.editor)
            self.resize_handle.update_position()
            
    def remove_handle(self):
        """
        Description: Removes the ResizeHandle from the scene.
        """
        if self.resize_handle:
            self.scene().removeItem(self.resize_handle)
            self.resize_handle = None
    

class PrimitiveHandle(QGraphicsRectItem):
    def __init__(self, parent_item, editor_ref):
        super().__init__(0, 0, 10, 10, parent_item)
        self.parent_item = parent_item
        self.editor = editor_ref
        self.setBrush(QBrush(QColor(0, 0, 255, 255)))
        self.setPen(QPen(Qt.white))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsSelectable)
        self.setZValue(99999)
        self.start_size = (50, 50)

    def update_position(self):
        """Se coloca en la esquina inferior derecha del padre"""
        rect = self.parent_item.pixmap().rect()
        self.setPos(rect.width() - 5, rect.height() - 5)

    def mousePressEvent(self, event):
        data = self.parent_item.obj_data
        self.start_size = (data.get('width', 50), data.get('height', 50))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        data = self.parent_item.obj_data
        end_w = data.get('width', 50)
        end_h = data.get('height', 50)
        
        if self.start_size != (end_w, end_h):
            self.editor.refresh_ui_for_object(data)
            print(f"Resize terminado: {end_w}x{end_h}")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            
            new_w = max(1, int(new_pos.x() + 5))
            new_h = max(1, int(new_pos.y() + 5))
            
            obj_data = self.parent_item.obj_data
            obj_data['width'] = new_w
            obj_data['height'] = new_h

            self.editor.update_canvas_from_resize(obj_data, self.parent_item)

            return new_pos
            
        return super().itemChange(change, value)