from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QGridLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
import subprocess
import functools
import os

try:
    from animated_button import AnimatedButton
except Exception:
    AnimatedButton = None


class ApplicationMenu(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Grid for app icons
        grid = QGridLayout()
        grid.setSpacing(10)  # tighter spacing
        grid.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(grid, stretch=0)
        main_layout.setAlignment(grid, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


        # Paths
        base_dir = os.path.dirname(__file__)
        programs_file = os.path.join(base_dir, "programs.txt")
        icons_dir = os.path.join(base_dir, "icons")

        row, col = 0, 0
        max_columns = 5  # 5 apps per row

        if os.path.exists(programs_file):
            with open(programs_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "|" not in line:
                        continue

                    parts = [p.strip() for p in line.split("|")]
                    name = parts[0]
                    command = parts[1]
                    icon_file = parts[2] if len(parts) > 2 else None

                    if icon_file:
                        icon_path = os.path.join(icons_dir, icon_file)
                        if os.path.exists(icon_path):
                            # Use AnimatedButton with faster animation for tiles
                            if AnimatedButton:
                                btn = AnimatedButton(
                                    "",
                                    lambda cmd=command: self.launch_program(cmd),
                                    animation_speed=100  # faster clicks for apps
                                )
                                btn.setIcon(QIcon(icon_path))
                                btn.setIconSize(QSize(200, 300))
                                btn.setFixedSize(200, 300)  # enforce 2:3 ratio
                                btn.set_tile_mode()  # Enable tile mode for icon buttons
                            else:
                                btn = QPushButton("")
                                btn.setIcon(QIcon(icon_path))
                                btn.setIconSize(QSize(200, 300))
                                btn.setFixedSize(200, 300)
                                btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                                # Apply tile-like style for fallback
                                btn.setStyleSheet("""
                                    QPushButton {
                                        background: transparent;
                                        border: none;
                                    }
                                    QPushButton:hover {
                                        background-color: rgba(255,255,255,0.08);
                                        border-radius: 12px;
                                    }
                                """)
                                btn.clicked.connect(lambda _, cmd=command: self.launch_program(cmd))
                        else:
                            btn = self._make_text_button(name, command)
                    else:
                        btn = self._make_text_button(name, command)

                    grid.addWidget(btn, row, col)

                    # Next column/row
                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1
        else:
            error_label = QLabel("⚠ programs.txt not found")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(error_label)

    def _make_text_button(self, name, command):
        """Fallback text button if no icon is available."""
        from PyQt6.QtWidgets import QPushButton
        if AnimatedButton:
            try:
                return AnimatedButton(name, lambda: self.launch_program(command))
            except TypeError:
                btn = AnimatedButton(name)
                btn.clicked.connect(lambda: self.launch_program(command))
                return btn
        else:
            btn = QPushButton(name)
            btn.clicked.connect(lambda: self.launch_program(command))
            return btn

    def launch_program(self, command):
        """Launch a program in the background."""
        try:
            subprocess.Popen(command.split())
            print(f"Launched: {command}")
        except Exception as e:
            print(f"Error launching {command}: {e}")