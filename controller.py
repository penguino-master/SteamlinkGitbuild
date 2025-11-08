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
            return  # Or switch to evdev here if you want (see bonus below)

        # Safety check: Does it have hats? (Xbox D-pad is hat 0)
        num_hats = joystick.get_numhats()
        if num_hats == 0:
            print("Warning: No hats detected—falling back to axis polling for D-pad.")
            self.use_axis_fallback = True
        else:
            print(f"Hats available: {num_hats}")
            self.use_axis_fallback = False

        # Quick fix: Pygame needs a display for reliable joystick events
        screen = pygame.display.set_mode((1, 1))  # Tiny, invisible surface

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():  # Event-driven: Safer than raw polling
                if event.type == pygame.QUIT:
                    running = False
                    break

                # Hat events (D-pad)
                elif event.type == pygame.JOYHATMOTION:
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

                # Button events (A/B)
                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    now = time.time()
                    if button not in self.last_button_time or now - self.last_button_time[button] > self.debounce_delay:
                        self.last_button_time[button] = now
                        if button == 0:  # A = Enter
                            QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Return))
                        elif button == 1:  # B = Esc/Back
                            QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Escape))

            # Fallback polling for axes (if no hats, e.g., some BT quirks)
            if self.use_axis_fallback:
                axis_y = joystick.get_axis(1)  # Left stick Y (Xbox standard)
                deadzone = 0.3
                if abs(axis_y) > deadzone:
                    direction = Qt.Key.Key_Up if axis_y < -deadzone else Qt.Key.Key_Down
                    now = time.time()
                    if now - self.last_hat_time > self.debounce_delay:
                        self.last_hat_time = now
                        QTimer.singleShot(0, lambda d=direction: self.gui.handle_key(d))
                # Add X axis for left/right if needed (e.g., axis 0 for horizontal)

            pygame.event.pump()  # Keep SDL alive
            clock.tick(60)  # Smoother polling

        pygame.quit()