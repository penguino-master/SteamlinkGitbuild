# NOTE: This script attempts to scan for Bluetooth devices using `bluetoothctl`.
# If running in a virtual machine or on a system without a Bluetooth adapter,
# the scanning thread may hang or produce no output.
# To avoid this during development, the actual Bluetooth scanning can be commented out.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import subprocess
import time


# class BluetoothScanner(QThread):
#     result_ready = pyqtSignal(list)

#     def run(self):
#         devices = []
#         start_time = time.time()
#         try:
#             process = subprocess.Popen("bluetoothctl devices", shell=True, stdout=subprocess.PIPE, text=True)
#             while True:
#                 if process.poll() is not None:
#                     break
#                 if time.time() - start_time > 10:
#                     process.terminate()
#                     break
#                 time.sleep(0.1)

#             if process.stdout:
#                 output = process.stdout.read()
#                 for line in output.strip().split("\n"):
#                     if line.startswith("Device"):
#                         parts = line.split(" ", 2)
#                         if len(parts) >= 3:
#                             address, name = parts[1], parts[2]
#                             devices.append({"name": name, "address": address, "connected": False})
#         except subprocess.SubprocessError:
#             pass

#         self.result_ready.emit(devices)


class BluetoothMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.title = QLabel("Available Devices")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.status_label = QLabel("Scanning...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.table = None

        # Trigger first scan
        self.scan_devices()

    def clear_table(self):
        if self.table:
            self.layout.removeWidget(self.table)
            self.table.deleteLater()
            self.table = None

    def scan_devices(self):
        self.status_label.setText("(Bluetooth scan disabled in VM)")
        self.clear_table()

        # Dummy placeholder data
        dummy_devices = [
            {"name": "Test Device 1", "connected": False},
            {"name": "Test Device 2", "connected": True}
        ]
        self._load_devices(dummy_devices)

    def _load_devices(self, devices):
        self.status_label.setText("")

        if not devices:
            self.status_label.setText("No devices found.")
            return

        self.table = QTableWidget(len(devices), 4)
        self.table.setHorizontalHeaderLabels(["Device Name", "Action", "Status", "Connect"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, device in enumerate(devices):
            name = device.get("name", "Unknown")
            connected = device.get("connected", False)
            status = "✓" if connected else "X"
            action_text = "Disconnect" if connected else "Connect"

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setCellWidget(row, 1, QPushButton(action_text))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            self.table.setCellWidget(row, 3, QPushButton("Connect"))

        self.layout.addWidget(self.table)

    def refresh(self):
        self.scan_devices()
