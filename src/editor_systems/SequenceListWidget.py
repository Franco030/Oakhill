from PySide6.QtWidgets import QListWidget, QAbstractItemView
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QBrush
from PySide6.QtCore import Qt, QRect, QPointF

COL_BG_DEFAULT = QColor("#1e1e1e")
COL_TEXT       = QColor("#d4d4d4")

COL_CHOICE  = QColor("#1a2b40")
COL_EXIT    = QColor("#3d1212")
COL_LABEL   = QColor("#2d1a36")

COL_JUMP_FALSE = QColor("#4a1818")
COL_LBL_FALSE  = QColor("#290e0e")
LINE_FALSE     = QColor("#ff5555")

COL_JUMP_TRUE  = QColor("#1b3a1b")
COL_LBL_TRUE   = QColor("#0e1f0e")
LINE_TRUE      = QColor("#55ff55") 

COL_JUMP_NEUTRO = QColor("#3e2723")
LINE_NEUTRO     = QColor("#ffaa00")

class SequenceListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSpacing(2)
        self.setAlternatingRowColors(False)

    def apply_logic_coloring(self):
        count = self.count()
        if count == 0: return

        label_map_items = {} 

        for i in range(count):
            item = self.item(i)

            item.setBackground(QBrush(COL_BG_DEFAULT)) 
            item.setForeground(QBrush(COL_TEXT)) 
            
            data = item.data(Qt.UserRole)
            if not data: continue

            action = data.get("action")
            params = data.get("params", "")

            if action == "Label":
                name = self._extract_param(params, "name") or self._extract_param(params, "id")
                if name: label_map_items[name] = item
                item.setBackground(QBrush(COL_LABEL))
            
            elif action == "AskChoice":
                item.setBackground(QBrush(COL_CHOICE))
            elif action == "Exit":
                item.setBackground(QBrush(COL_EXIT))

        for i in range(count):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if not data: continue
            
            action = data.get("action")
            params = data.get("params", "")

            if action in ["JumpIfTrue", "JumpIfFalse", "Jump"]:
                target = self._extract_param(params, "target") or self._extract_param(params, "label")
                
                if action == "JumpIfFalse":
                    item.setBackground(QBrush(COL_JUMP_FALSE))
                    if target and target in label_map_items:
                        label_map_items[target].setBackground(QBrush(COL_LBL_FALSE))
                
                elif action == "JumpIfTrue":
                    item.setBackground(QBrush(COL_JUMP_TRUE))
                    if target and target in label_map_items:
                        label_map_items[target].setBackground(QBrush(COL_LBL_TRUE))
                
                elif action == "Jump":
                    item.setBackground(QBrush(COL_JUMP_NEUTRO))

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        count = self.count()
        if count == 0: return

        label_map_idx = {}
        jumps = []

        for i in range(count):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if not data: continue
            
            action = data.get("action")
            params = data.get("params", "")
            
            if action == "Label":
                name = self._extract_param(params, "name") or self._extract_param(params, "id")
                if name: label_map_idx[name] = i
            elif action in ["JumpIfTrue", "JumpIfFalse", "Jump"]:
                target = self._extract_param(params, "target") or self._extract_param(params, "label")
                if target: jumps.append((i, target, action))

        for jump_idx, target_name, jump_type in jumps:
            if target_name in label_map_idx:
                target_idx = label_map_idx[target_name]
                self._draw_connection(painter, jump_idx, target_idx, jump_type)

    def _draw_connection(self, painter, start_idx, end_idx, jump_type):
        rect_start = self.visualItemRect(self.item(start_idx))
        rect_end = self.visualItemRect(self.item(end_idx))

        if not rect_start.isValid() and not rect_end.isValid(): return

        color = LINE_NEUTRO
        if jump_type == "JumpIfTrue": color = LINE_TRUE
        elif jump_type == "JumpIfFalse": color = LINE_FALSE

        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.setBrush(Qt.NoBrush)

        offset_depth = (start_idx % 5) * 5
        x_base = self.viewport().width() - 25 - offset_depth
        y_start = rect_start.center().y()
        y_end = rect_end.center().y()

        path = QPainterPath()
        path.moveTo(rect_start.right() - 20, y_start)
        
        ctrl1_x, ctrl1_y = x_base, y_start
        ctrl2_x, ctrl2_y = x_base, y_end
        
        path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, rect_end.right() - 20, y_end)
        
        painter.drawPath(path)
        
        painter.setBrush(color)
        painter.drawEllipse(QPointF(rect_end.right() - 20, y_end), 3, 3)

    def _extract_param(self, param_str, key):
        if not param_str: return None
        pairs = param_str.replace('\n', ';').split(';')
        for p in pairs:
            if '=' in p:
                k, v = p.split('=', 1)
                if k.strip() == key:
                    return v.strip()
        return None