# menu_system.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
import subprocess
import shutil

# Try importing your AnimatedButton. If it doesn't match the expected
# constructor or isn't available, we'll gracefully fall back.
try:
    from animated_button import AnimatedButton
except Exception:
    AnimatedButton = None


class SystemMenu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 20px top and left margins (already correct)
        layout.setSpacing(10)

        # Title
        title = QLabel("System Options")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # --- Top buttons row (Restart / Shutdown / Exit) ---
        # Use AnimatedButton if possible, otherwise fallback to QPushButton.
        top_row = QHBoxLayout()
        restart_btn = self._make_button("Restart Machine", lambda: subprocess.Popen(["sudo", "reboot"]))
        shutdown_btn = self._make_button("Shutdown Machine", lambda: subprocess.Popen(["sudo", "shutdown", "now"]))
        exit_btn = self._make_button("Exit App", self.close_app)

        top_row.addWidget(restart_btn)
        top_row.addWidget(shutdown_btn)
        top_row.addWidget(exit_btn)
        layout.addLayout(top_row)

        layout.addStretch()  # push everything to top

    def _make_button(self, label, callback):
        """
        Helper: try to construct an AnimatedButton with (label, callback).
        If that fails or AnimatedButton is not available, create a normal QPushButton.
        This aims to be resilient against different AnimatedButton signatures.
        """
        if AnimatedButton:
            try:
                # Preferred: AnimatedButton(label, callback)
                btn = AnimatedButton(label, callback)
                return btn
            except TypeError:
                # Some AnimatedButton variants might accept only label or different args.
                # Try AnimatedButton(label) then connect clicked.
                try:
                    btn = AnimatedButton(label)
                    try:
                        btn.clicked.connect(callback)
                    except Exception:
                        # If it doesn't have .clicked or it's handled internally, ignore
                        pass
                    return btn
                except Exception:
                    pass

        # Fallback: standard QPushButton
        btn = QPushButton(label)
        btn.clicked.connect(callback)
        return btn

    def apply_resolution(self):
        """
        Apply the selected resolution using Raspberry Pi's tvservice + fbset.
        Runs only when tvservice is available (Apply button is disabled otherwise).
        """
        if not shutil.which("tvservice"):
            print("tvservice not found; skipping resolution change.")
            return

        mode = self.res_dropdown.currentData()
        try:
            if mode == "1080p":
                # 1080p60 (DMT mode 82)
                subprocess.run(["tvservice", "-e", "DMT 82 HDMI"], check=True)
                subprocess.run(["fbset", "-depth", "8"], check=True)
                subprocess.run(["fbset", "-depth", "16"], check=True)
            elif mode == "1440p":
                # 1440p (beta) - DMT 51 is commonly used for 2560x1440 modes,
                # behaviour may vary depending on Pi firmware and display.
                subprocess.run(["tvservice", "-e", "DMT 51 HDMI"], check=True)
                subprocess.run(["fbset", "-depth", "8"], check=True)
                subprocess.run(["fbset", "-depth", "16"], check=True)
            print(f"Applied resolution mode: {mode}")
        except subprocess.CalledProcessError as e:
            print("Error applying resolution:", e)

    def close_app(self):
        # Close the main window (same as Exit button behavior previously)
        self.window().close()
