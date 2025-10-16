from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
import subprocess
import re
import shutil

try:
    from animated_button import AnimatedButton
except Exception:
    AnimatedButton = None


class VolumeMenu(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Added 20px top margin
        layout.setSpacing(10)

        # Title
        title = QLabel("Volume Control")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # --- Top button row ---
        btn_row = QHBoxLayout()
        vol_up = self._make_button("Volume +", lambda: self.change_volume(+5))
        vol_down = self._make_button("Volume -", lambda: self.change_volume(-5))
        self.mute_btn = self._make_button("Mute", self.toggle_mute)

        btn_row.addWidget(vol_down)
        btn_row.addWidget(vol_up)
        btn_row.addWidget(self.mute_btn)

        layout.addLayout(btn_row)

        # --- Volume bar ---
        self.volume_bar = QProgressBar()
        self.volume_bar.setMaximum(100)
        self.volume_bar.setTextVisible(True)
        self.volume_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Style the bar for a cleaner, modern look
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #2c2f33;
                text-align: center;
                height: 25px;
                font-size: 16px;
            }
            QProgressBar::chunk {
                background-color: #7289da;
                border-radius: 8px;
            }
        """)

        layout.addWidget(self.volume_bar)

        # Timer to update volume continuously
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_volume)
        self.timer.start(1000)

        self.update_volume()

        layout.addStretch()

    def _make_button(self, label, callback):
        """Creates an AnimatedButton if available, otherwise QPushButton."""
        from PyQt6.QtWidgets import QPushButton
        if AnimatedButton:
            try:
                return AnimatedButton(label, callback)
            except TypeError:
                btn = AnimatedButton(label)
                btn.clicked.connect(callback)
                return btn
        else:
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            return btn

    def change_volume(self, delta):
        """Increase or decrease volume using pactl if available."""
        if not shutil.which("pactl"):
            print("pactl not found, volume control not available.")
            return

        is_muted = self.get_mute_state()
        if is_muted:
            # Unmute first if currently muted
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])

        current = self.get_volume()
        if current is not None:
            new_volume = max(0, min(100, current + delta))
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{new_volume}%"])

        # Update immediately for responsiveness
        self.update_volume()

    def toggle_mute(self):
        if not shutil.which("pactl"):
            print("pactl not found, mute not available.")
            return
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        # Update immediately for responsiveness
        self.update_volume()

    def get_volume(self):
        try:
            result = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                                    capture_output=True, text=True)
            match = re.search(r'(\d+)%', result.stdout)
            return int(match.group(1)) if match else None
        except Exception:
            return None

    def get_mute_state(self):
        try:
            result = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                                    capture_output=True, text=True)
            return "Mute: yes" in result.stdout
        except Exception:
            return False

    def update_volume(self):
        current = self.get_volume()
        is_muted = self.get_mute_state()
        if is_muted:
            self.volume_bar.setValue(0)
            self.volume_bar.setFormat("Muted")
            self.mute_btn.setText("Unmute")
        elif current is not None:
            self.volume_bar.setValue(current)
            self.volume_bar.setFormat(f"{current}%")
            self.mute_btn.setText("Mute")
        else:
            self.volume_bar.setFormat("Unknown")
            self.mute_btn.setText("Mute")