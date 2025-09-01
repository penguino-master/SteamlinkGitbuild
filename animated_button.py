from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer


class AnimatedButton(QPushButton):
    def __init__(self, label: str = "", action_callback=None, animation_speed=300, parent=None):
        # Back-compat: allow signature (label, callback, parent)
        if parent is None and not isinstance(animation_speed, (int, float)):
            parent = animation_speed
            animation_speed = 300

        super().__init__(label, parent)

        self.action_callback = action_callback
        self.animation_speed = int(animation_speed)
        self._anim = None
        self._hover_anim = None
        self._orig_rect = None
        self.is_tile = False  # set to True via set_tile_mode() for app tiles

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Default style for normal menu buttons
        self.setStyleSheet(self.button_style(focused=False))

        if self.action_callback:
            # Prevent Qt from passing a bool
            self.clicked.connect(lambda *_: self.action_callback())

    # ---- Styles ----
    def button_style(self, focused=False) -> str:
        border = "2px solid #1e90ff;" if focused else "none;"
        return f"""
        QPushButton {{
            background-color: #0078d4;
            color: white;
            border: {border}
            border-radius: 12px;
            padding: 10px 16px;
        }}
        QPushButton:focus {{ outline: none; }}
        """

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Treat Enter/Return the same as clicking the button
            self.click()
            return
        super().keyPressEvent(event)


    def set_tile_mode(self):
        """Use this for icon tiles in the Applications grid."""
        self.is_tile = True
        self.setStyleSheet("""
        QPushButton {
            background: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255,255,255,0.08);
            border-radius: 12px;
        }
        """)

    # ---- Animation helpers ----
    def animate_geometry(self, end_rect: QRect):
        g = self.geometry()
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(max(60, min(600, self.animation_speed)))
        anim.setStartValue(g)
        anim.setEndValue(end_rect)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        return anim

    # ---- Events ----
    def resizeEvent(self, e):
        # Track the true layout-driven geometry to restore to
        self._orig_rect = self.geometry()
        super().resizeEvent(e)

    def mousePressEvent(self, e):
        if self._orig_rect:
            g = self._orig_rect
            # Shrink ~10% around center
            shrink_w, shrink_h = int(g.width() * 0.9), int(g.height() * 0.9)
            shrink_x = g.x() + (g.width() - shrink_w) // 2
            shrink_y = g.y() + (g.height() - shrink_h) // 2
            self._anim = self.animate_geometry(QRect(shrink_x, shrink_y, shrink_w, shrink_h))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        if self._orig_rect:
            # Ensure Qt isn't holding a pressed/checked visual
            self.setDown(False)
            self.setChecked(False)

            # Restore to exact original size/pos right after Qt processes release
            QTimer.singleShot(0, lambda: self.animate_geometry(self._orig_rect))

            # Reapply the correct style
            if self.is_tile:
                self.set_tile_mode()
            else:
                self.setStyleSheet(self.button_style(focused=self.hasFocus()))

    def enterEvent(self, e):
        # Only tiles get hover zoom
        if self.is_tile and self._orig_rect:
            g = self._orig_rect
            zoom_w, zoom_h = int(g.width() * 1.08), int(g.height() * 1.08)
            zoom_x = g.x() - (zoom_w - g.width()) // 2
            zoom_y = g.y() - (zoom_h - g.height()) // 2
            self._hover_anim = self.animate_geometry(QRect(zoom_x, zoom_y, zoom_w, zoom_h))
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self.is_tile and self._orig_rect:
            self._hover_anim = self.animate_geometry(self._orig_rect)
        super().leaveEvent(e)

    def focusInEvent(self, e):
        if self.is_tile:
            # Blue border focus for tiles
            self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #1e90ff;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            """)
        else:
            # Blue border focus for menu buttons
            self.setStyleSheet(self.button_style(focused=True))
        super().focusInEvent(e)

    def focusOutEvent(self, e):
        if self.is_tile:
            self.set_tile_mode()
        else:
            self.setStyleSheet(self.button_style(focused=False))
        super().focusOutEvent(e)
