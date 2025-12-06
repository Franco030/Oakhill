from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap, QPainter
from PySide6.QtCore import Qt, QRectF, QPointF
import copy
from .EditorCommands import CmdTransform, CmdResize # Asegúrate de tener CmdResize en EditorCommands

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent_item, editor_ref):
        super().__init__(0, 0, 10, 10, parent_item)
        self.parent_item = parent_item
        self.editor = editor_ref
        
        self.setBrush(QBrush(QColor(0, 0, 255, 255)))
        self.setPen(QPen(Qt.white))
        
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        self.setZValue(99999)
        self.start_size = (50, 50)
        
        self.update_position()

    def update_position(self):
        """Se pega a la esquina inferior derecha del padre."""
        if self.parent_item.pixmap():
            rect = self.parent_item.pixmap().rect()
            self.setPos(rect.width() - 5, rect.height() - 5)

    def mousePressEvent(self, event):
        data = self.parent_item.obj_data
        self.start_size = (data.get('width', 50), data.get('height', 50))
        event.accept()

    def mouseMoveEvent(self, event):
        mouse_pos_in_parent = self.mapToParent(event.pos())
        
        new_w = max(1, int(mouse_pos_in_parent.x() + 5))
        new_h = max(1, int(mouse_pos_in_parent.y() + 5))
        
        obj_data = self.parent_item.obj_data
        obj_data['width'] = new_w
        obj_data['height'] = new_h
        
        self.editor.update_canvas_from_resize(obj_data, self.parent_item)

        self.update_position()
        
        event.accept()

    def mouseReleaseEvent(self, event):
        data = self.parent_item.obj_data
        end_w = int(data.get('width', 50))
        end_h = int(data.get('height', 50))

        if self.start_size != (end_w, end_h):
            self.editor.refresh_ui_for_object(data)
        
        event.accept()

class HitboxHandle(QGraphicsRectItem):
    """
    Handle amarillo para redimensionar el Hitbox rojo.
    Modifica collision_rect_offset (dw, dh).
    """
    def __init__(self, parent_hitbox, editor_ref):
        super().__init__(0, 0, 10, 10, parent_hitbox)
        self.parent_hitbox = parent_hitbox
        self.editor = editor_ref
        
        # Color Amarillo para diferenciarlo del Azul (Primitivas)
        self.setBrush(QBrush(QColor(255, 255, 0, 255))) 
        self.setPen(QPen(Qt.black))
        
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(99999)
        
        self.update_position()

    def update_position(self):
        rect = self.parent_hitbox.rect()
        self.setPos(rect.width() - 5, rect.height() - 5)

    def mousePressEvent(self, event):
        data = self.parent_hitbox.obj_data
        self.start_offset = copy.deepcopy(data.get('collision_rect_offset', [0,0,0,0]))
        event.accept()

    def mouseMoveEvent(self, event):
        mouse_pos = self.mapToParent(event.pos())
        
        new_w = max(10, int(mouse_pos.x() + 5))
        new_h = max(10, int(mouse_pos.y() + 5))
        
        self.parent_hitbox.setRect(0, 0, new_w, new_h)
        self.update_position()
        
        sprite_item = self.parent_hitbox.parent_sprite
        if sprite_item and sprite_item.pixmap():
            sprite_w = sprite_item.pixmap().width()
            sprite_h = sprite_item.pixmap().height()
            
            new_dw = int(new_w - sprite_w)
            new_dh = int(new_h - sprite_h)
            
            obj_data = self.parent_hitbox.obj_data
            current_off = obj_data.get('collision_rect_offset', [0,0,0,0])
            
            obj_data['collision_rect_offset'] = [current_off[0], current_off[1], new_dw, new_dh]
            
            self.editor.sync_hitbox_size_ui(new_dw, new_dh)

        event.accept()

    def mouseReleaseEvent(self, event):
        data = self.parent_hitbox.obj_data
        end_offset = data.get('collision_rect_offset', [0,0,0,0])
        
        if self.start_offset != end_offset:
            cmd = CmdTransform(self.editor, data, 
                             (data['x'], data['y']), (data['x'], data['y']), # Posición no cambia
                             self.start_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)
        
        event.accept()

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

    def mousePressEvent(self, event):
        self.start_pos_offset = copy.deepcopy(self.obj_data.get('collision_rect_offset', [0,0,0,0]))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        end_offset = self.obj_data.get('collision_rect_offset', [0,0,0,0])
        if self.start_pos_offset != end_offset and self.editor:
            cmd = CmdTransform(self.editor, self.obj_data, 
                             (self.obj_data['x'], self.obj_data['y']), 
                             (self.obj_data['x'], self.obj_data['y']), 
                             self.start_pos_offset, end_offset)
            self.editor.undo_manager.push(cmd, execute_now=False)

    def add_resize_handle(self):
        if not self.resize_handle:
            self.resize_handle = HitboxHandle(self, self.editor)

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
        self.resize_handle = None 
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
    
    def create_primitive_handle(self):
        if self.obj_data.get("type") == "Primitive" and not self.resize_handle:
            self.resize_handle = ResizeHandle(self, self.editor)
            self.resize_handle.update_position()
            
    def remove_handle(self):
        if self.resize_handle:
            if self.scene() and self.resize_handle.scene() == self.scene():
                self.scene().removeItem(self.resize_handle)
            self.resize_handle = None

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
            cmd = CmdTransform(self.editor, self.obj_data, 
                             (self.start_x, self.start_y), (end_x, end_y), 
                             offset, offset)
            self.editor.undo_manager.push(cmd, execute_now=False)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.create_primitive_handle()
            else:
                if self.resize_handle and self.resize_handle.isUnderMouse():
                    self.setSelected(True)
                    return
                
                self.remove_handle()

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