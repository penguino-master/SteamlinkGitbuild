import pygame
from threading import Thread
import time
from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication


class ControllerThread(Thread):
    def __init__(self, gui):
        super().__init__(daemon=True)
        self.gui = gui

    def run(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            return

        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        clock = pygame.time.Clock()

        while True:
            pygame.event.pump()
            hat = joystick.get_hat(0)
            axis_y = joystick.get_axis(1)

            # Up / Down
            if hat[1] == 1 or axis_y < -0.5:
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Up))
                time.sleep(0.2)
            elif hat[1] == -1 or axis_y > 0.5:
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Down))
                time.sleep(0.2)

            # Left / Right
            if hat[0] == -1:
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Left))
                time.sleep(0.2)
            elif hat[0] == 1:
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Right))
                time.sleep(0.2)

            # A button = Enter
            if joystick.get_button(0):
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Return))
                time.sleep(0.25)

            # B button = Escape (could be mapped to "back" later)
            if joystick.get_button(1):
                QTimer.singleShot(0, lambda: self.gui.handle_key(Qt.Key.Key_Escape))
                time.sleep(0.25)

            clock.tick(30)