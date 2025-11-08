import pygame
from threading import Thread
import time
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeyEvent  # For simulating keys

class ControllerThread(Thread):
    def __init__(self, gui):
        super().__init__(daemon=True)
        self.gui = gui
        self.last_hat_time = 0
        self.last_button_time = {}  # Per-button debounce
        self.debounce_delay = 0.15  # Faster for Zero 2 W

    def run(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joysticks found—check Bluetooth!")
            return

        joystick = None
        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Controller detected: {joystick.get_name()}")
        except Exception as e:
            print(f"Joystick init failed: {e} — Falling back to no controller support.")
            return

        # Safety check: Does it have hats? (Xbox D-pad is hat 0)
        num_hats = joystick.get_numhats()
        if num_hats == 0:
            print("Warning: No hats detected—falling back to axis polling for D-pad.")
            self.use_axis_fallback = True
        else:
            print(f"Hats available: {num_hats}")
            self.use_axis_fallback = False

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():  # Event-driven: Safer than raw polling
                if event.type == pygame.QUIT:
                    running = False
                    break

                # Hat events (D-pad) — if available
                elif event.type == pygame.JOYHATMOTION and not self.use_axis_fallback:
                    if num_hats > event.hat:  # Valid hat index
                        hat_pos = event.value  # (-1/0/1, -1/0/1)
                        now = time.time()
                        if now - self.last_hat_time > self.debounce_delay:
                            self.last_hat_time = now
                            if hat_pos == (0, 1):  # Up
                                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Up))
                            elif hat_pos == (0, -1):  # Down
                                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Down))
                            elif hat_pos == (-1, 0):  # Left
                                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Left))
                            elif hat_pos == (1, 0):  # Right
                                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Right))

                # Button events (A/B) — always active
                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    now = time.time()
                    if button not in self.last_button_time or now - self.last_button_time[button] > self.debounce_delay:
                        self.last_button_time[button] = now
                        if button == 0:  # A = Enter
                            QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Return))
                        elif button == 1:  # B = Esc/Back
                            QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Escape))

            # Enhanced fallback: Poll axes for D-pad emulation (Xbox BT standard)
            if self.use_axis_fallback and joystick:
                deadzone = 0.3  # Tune for stick drift (higher = less sensitive)
                axis_x = joystick.get_axis(0)  # Left stick X (left/right)
                axis_y = joystick.get_axis(1)  # Left stick Y (up/down)

                now = time.time()
                if now - self.last_hat_time > self.debounce_delay:
                    # Horizontal (Left/Right)
                    if abs(axis_x) > deadzone:
                        direction = Qt.Key.Key_Left if axis_x < -deadzone else Qt.Key.Key_Right
                        self.last_hat_time = now
                        QTimer.singleShot(0, lambda d=direction: self.gui.handle_key(d))

                    # Vertical (Up/Down) — only if no horizontal to avoid conflicts
                    elif abs(axis_y) > deadzone:
                        direction = Qt.Key.Key_Up if axis_y < -deadzone else Qt.Key.Key_Down
                        self.last_hat_time = now
                        QTimer.singleShot(0, lambda d=direction: self.gui.handle_key(d))

            pygame.event.pump()  # Keep SDL alive (no display needed)
            clock.tick(60)  # Smooth 60 FPS polling, low CPU on Zero 2 W

        pygame.quit()