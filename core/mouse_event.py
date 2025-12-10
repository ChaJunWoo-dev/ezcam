from PyQt6.QtCore import Qt, QPoint, QRect

class MouseEvent:
    EDGE_MARGIN = 10

    def __init__(self):
        self.drag_pos = None
        self.resizing = False
        self.resize_dir = None
        self.resize_start_geo = None
        self.ctrl_resize_mode = False
        self.ctrl_resize_start_pos = None
        self.ctrl_resize_start_size = None
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.ctrl_resize_mode = True
            self.ctrl_resize_start_pos = event.globalPosition().toPoint()
            self.ctrl_resize_start_size = self.size()
            event.accept()
            return

        pos = event.position()
        rect = self.rect()
        margin = self.EDGE_MARGIN

        x, y = pos.x(), pos.y()
        left, right = rect.left(), rect.right()
        top, bottom = rect.top(), rect.bottom()

        on_left = left <= x <= left + margin
        on_right = right - margin <= x <= right
        on_top = top <= y <= top + margin
        on_bottom = bottom - margin <= y <= bottom

        self.resizing = False
        self.resize_dir = None
        self.resize_start_geo = None

        resize_dir = None

        if on_right and on_bottom:
            resize_dir = "bottom-right"
        elif on_left and on_bottom:
            resize_dir = "bottom-left"
        elif on_right and on_top:
            resize_dir = "top-right"
        elif on_left and on_top:
            resize_dir = "top-left"
        elif on_right:
            resize_dir = "right"
        elif on_left:
            resize_dir = "left"
        elif on_bottom:
            resize_dir = "bottom"
        elif on_top:
            resize_dir = "top"

        if resize_dir:
            self.resizing = True
            self.resize_dir = resize_dir
            self.resize_start_geo = self.geometry()
        else:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.ctrl_resize_mode:
                delta = event.globalPosition().toPoint() - self.ctrl_resize_start_pos
                new_width = max(100, self.ctrl_resize_start_size.width() + delta.x())
                new_height = max(100, self.ctrl_resize_start_size.height() + delta.y())
                self.resize(new_width, new_height)
                event.accept()
            elif self.resizing:
                self._handle_resize(event)
            elif self.drag_pos:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
        else:
            self._update_cursor(event)

    def _update_cursor(self, event):
        pos = event.position()
        rect = self.rect()
        margin = self.EDGE_MARGIN

        x, y = pos.x(), pos.y()
        left, right = rect.left(), rect.right()
        top, bottom = rect.top(), rect.bottom()

        on_left = left <= x <= left + margin
        on_right = right - margin <= x <= right
        on_top = top <= y <= top + margin
        on_bottom = bottom - margin <= y <= bottom

        if (on_right and on_bottom) or (on_left and on_top):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (on_left and on_bottom) or (on_right and on_top):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif on_left or on_right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif on_top or on_bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _handle_resize(self, event):
        if not self.resize_start_geo:
            return

        geo = self.geometry()
        gx, gy = int(event.globalPosition().x()), int(event.globalPosition().y())

        if "right" in self.resize_dir:
            geo.setWidth(max(100, gx - geo.x()))
        elif "left" in self.resize_dir:
            new_width = self.resize_start_geo.right() - gx
            if new_width >= 100:
                geo.setLeft(gx)

        if "bottom" in self.resize_dir:
            geo.setHeight(max(100, gy - geo.y()))
        elif "top" in self.resize_dir:
            new_height = self.resize_start_geo.bottom() - gy
            if new_height >= 100:
                geo.setTop(gy)

        self.setGeometry(geo)

    def mouseReleaseEvent(self, event):
        self.ctrl_resize_mode = False
        self.ctrl_resize_start_pos = None
        self.ctrl_resize_start_size = None
        self.drag_pos = None
        self.resizing = False
        self.resize_dir = None
        self.resize_start_geo = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
