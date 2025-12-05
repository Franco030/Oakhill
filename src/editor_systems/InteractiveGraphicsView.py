from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QListWidgetItem, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QListWidget, QInputDialog, QMessageBox, QAbstractItemView, QGraphicsView,
)
from PySide6.QtGui import QPixmap, QBrush, QColor, QPen, QKeySequence, QShortcut, QPainter
from PySide6.QtCore import Qt, QRectF, QPointF

class InteractiveGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.setRenderHint(QPainter.Antialiasing, False)
        self.setDragMode(QGraphicsView.NoDrag)
        self._is_panning = False
        self._last_mouse_pos = QPointF()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor

            current_scale = self.transform().m11()

            if event.angleDelta().y() > 0:
                if current_scale < 5.0:
                    self.scale(zoom_in_factor, zoom_in_factor)
            else:
                if current_scale > 0.1:
                    self.scale(zoom_out_factor, zoom_out_factor)
            
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and (event.modifiers() & Qt.ControlModifier):
            self._is_panning = True
            self._last_mouse_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position() - self._last_mouse_pos
            self._last_mouse_pos = event.position()

            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)