from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from controller import ControllerThread
from menu_bluetooth import BluetoothMenu
from menu_system import SystemMenu
from menu_volume import VolumeMenu
from menu_application import ApplicationMenu
from animated_button import AnimatedButton
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QKeyEvent
import socket


class SteamlinkGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steamlink Companion UI")

        # Force fullscreen flags BEFORE layout/show (works on LinuxFB/EGLFS)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()

        # Explicitly set resolution (1920x1080) - overrides framebuffer
        self.resize(1920, 1080)
        self.setFixedSize(1920, 1080)  # Lock it; no resizing accidents

        # Ensure it grabs the primary screen
        self.move(0, 0)  # Top-left origin

        # Kiosk polish: Hide cursor
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.raise_()  # Top if layered (rare on FB)

        # Layouts
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(20, 20, 0, 0)  # 20px top margin
        sidebar.setSpacing(10)

        self.pages = QStackedLayout()

        # Device Info
        device_label = QLabel("Steamlink Box")
        device_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        ip_label = QLabel("IPv4")
        ip_value = QLabel(self.get_ip_address())

        sidebar.addWidget(device_label)
        sidebar.addWidget(ip_label)
        sidebar.addWidget(ip_value)
        sidebar.addSpacing(10)

        # Menu buttons + page mapping
        self.menu_buttons = []
        self.page_map = {}

        buttons_info = [
            ("Launch Application", ApplicationMenu()),
            ("Bluetooth", BluetoothMenu()),
            ("Volume", VolumeMenu()),
            ("System", SystemMenu()),
        ]

        for i, (text, widget) in enumerate(buttons_info):
            btn = AnimatedButton(text, lambda t=text: self.switch_page(t), self)
            btn.setMinimumHeight(100)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

            sidebar.addWidget(btn)
            self.menu_buttons.append(btn)

            self.pages.addWidget(widget)
            self.page_map[text] = widget

        sidebar.addStretch()

        # Sidebar stretch for ~0.3x width
        layout.addLayout(sidebar, 1)
        layout.addLayout(self.pages, 4)

        # Default focus on first button
        if self.menu_buttons:
            self.menu_buttons[0].setFocus()

        # Controller handling
        def handle_key(self, key):
            """Simulate a key press for controller input."""
            event = QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier)
            self.keyPressEvent(event)

        # Controller input thread
        self.controller_thread = ControllerThread(self)
        self.controller_thread.start()

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unavailable"

    def switch_page(self, page_name):
        """Switch stacked layout to the page mapped to this name."""
        widget = self.page_map[page_name]
        self.pages.setCurrentWidget(widget)
        return widget

    # --- Navigation overrides ---
    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Right:
            # Enter current menu
            focused_btn = QApplication.focusWidget()
            if focused_btn in self.menu_buttons:
                page_name = focused_btn.text()
                page_widget = self.switch_page(page_name)

                # Move focus into first focusable child inside page
                first_child = page_widget.focusWidget()
                if not first_child:
                    btns = page_widget.findChildren(QPushButton)
                    if btns:
                        btns[0].setFocus()
                return

        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):
            # Back to menu selector (← or Esc)
            if QApplication.focusWidget() not in self.menu_buttons:
                current_page = self.pages.currentWidget()
                for name, widget in self.page_map.items():
                    if widget == current_page:
                        for btn in self.menu_buttons:
                            if btn.text() == name:
                                btn.setFocus()
                                return

        super().keyPressEvent(event)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gui = SteamlinkGUI()
    gui.show()
    sys.exit(app.exec())