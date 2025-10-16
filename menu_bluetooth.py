from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import subprocess
import time

try:
    from animated_button import AnimatedButton
except Exception:
    AnimatedButton = None


class DiscoverableScanner(QThread):
    devices_found = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        devices = []
        try:
            subprocess.run(["bluetoothctl", "agent", "on"], capture_output=True, timeout=5)
            subprocess.run(["bluetoothctl", "default-agent"], capture_output=True, timeout=5)
            subprocess.Popen(["bluetoothctl", "scan", "on"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(10)
            subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, timeout=5)
            result = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                if line.startswith("Device "):
                    parts = line.split(maxsplit=2)
                    if len(parts) == 3:
                        mac, name = parts[1], parts[2]
                        devices.append({"mac": mac, "name": name})
            # Filter out already paired devices
            paired_devices = self.parent().get_paired_devices()
            paired_macs = {d["mac"] for d in paired_devices}
            devices = [d for d in devices if d["mac"] not in paired_macs]
        except Exception:
            pass
        self.devices_found.emit(devices)


class BluetoothMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Added 20px top margin
        self.layout.setSpacing(10)

        # Title
        title = QLabel("Bluetooth Devices")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Status label for scanning
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Scan button
        self.scan_btn = self.create_animated_button("Scan for New Devices", self.start_discoverable_scan)
        self.layout.addWidget(self.scan_btn)

        self.discovered_table = None

        # Spacing
        self.layout.addSpacing(20)

        # Paired section title
        paired_title = QLabel("Paired Devices")
        paired_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(paired_title)

        # Refresh button for paired
        self.refresh_btn = self.create_animated_button("Refresh", self.refresh_paired)
        self.layout.addWidget(self.refresh_btn)

        self.paired_table = None

        # Initial load
        self.refresh_paired()

        self.layout.addStretch()

    def create_animated_button(self, label, callback):
        """Creates an AnimatedButton if available, otherwise QPushButton."""
        if AnimatedButton:
            return AnimatedButton(label, callback)
        else:
            from PyQt6.QtWidgets import QPushButton
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            return btn

    def start_discoverable_scan(self):
        self.status_label.setText("Scanning...")
        self.clear_discovered_table()
        self.scan_thread = DiscoverableScanner(self)
        self.scan_thread.devices_found.connect(self._load_discovered)
        self.scan_thread.start()

    def _load_discovered(self, devices):
        self.status_label.setText("")
        self.clear_discovered_table()
        if not devices:
            self.status_label.setText("No discoverable devices found.")
            return

        self.discovered_table = QTableWidget(len(devices), 3)
        self.discovered_table.setHorizontalHeaderLabels(["Name", "MAC Address", "Action"])
        self.discovered_table.verticalHeader().setVisible(False)
        self.discovered_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.discovered_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.discovered_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.discovered_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, dev in enumerate(devices):
            self.discovered_table.setItem(row, 0, QTableWidgetItem(dev["name"]))
            self.discovered_table.setItem(row, 1, QTableWidgetItem(dev["mac"]))
            pair_btn = self.create_animated_button("Pair", lambda m=dev["mac"]: self.pair_device(m))
            self.discovered_table.setCellWidget(row, 2, pair_btn)

        pos = self.layout.indexOf(self.scan_btn) + 1
        self.layout.insertWidget(pos, self.discovered_table)

    def clear_discovered_table(self):
        if self.discovered_table:
            self.layout.removeWidget(self.discovered_table)
            self.discovered_table.deleteLater()
            self.discovered_table = None

    def get_paired_devices(self):
        try:
            result = subprocess.run(["bluetoothctl", "paired-devices"], capture_output=True, text=True, timeout=5)
            devices = []
            for line in result.stdout.splitlines():
                if line.startswith("Device "):
                    parts = line.split(maxsplit=2)
                    if len(parts) == 3:
                        mac, name = parts[1], parts[2]
                        devices.append({"mac": mac, "name": name})
            return devices
        except Exception:
            return []

    def get_connected_macs(self):
        try:
            result = subprocess.run(["bluetoothctl", "devices Connected"], capture_output=True, text=True, timeout=5)
            macs = []
            for line in result.stdout.splitlines():
                if line.startswith("Device "):
                    parts = line.split()
                    if len(parts) >= 2:
                        macs.append(parts[1])
            return macs
        except Exception:
            return []

    def refresh_paired(self):
        self.clear_paired_table_and_label()
        paired_pos = self.layout.indexOf(self.refresh_btn) + 1
        paired = self.get_paired_devices()
        if not paired:
            self.no_paired_label = QLabel("No paired devices.")
            self.no_paired_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.insertWidget(paired_pos, self.no_paired_label)
            return

        connected_macs = set(self.get_connected_macs())
        self.paired_table = QTableWidget(len(paired), 5)
        self.paired_table.setHorizontalHeaderLabels(["Name", "MAC Address", "Status", "Action", "Forget"])
        self.paired_table.verticalHeader().setVisible(False)
        self.paired_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.paired_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.paired_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.paired_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, dev in enumerate(paired):
            dev["connected"] = dev["mac"] in connected_macs
            self.paired_table.setItem(row, 0, QTableWidgetItem(dev["name"]))
            self.paired_table.setItem(row, 1, QTableWidgetItem(dev["mac"]))
            status = "Connected" if dev["connected"] else "Disconnected"
            self.paired_table.setItem(row, 2, QTableWidgetItem(status))
            action_text = "Disconnect" if dev["connected"] else "Connect"
            action_btn = self.create_animated_button(action_text, lambda m=dev["mac"]: self.toggle_connection(m))
            self.paired_table.setCellWidget(row, 3, action_btn)
            forget_btn = self.create_animated_button("Forget", lambda m=dev["mac"]: self.forget_device(m))
            self.paired_table.setCellWidget(row, 4, forget_btn)

        self.layout.insertWidget(paired_pos, self.paired_table)

    def clear_paired_table_and_label(self):
        if self.paired_table:
            self.layout.removeWidget(self.paired_table)
            self.paired_table.deleteLater()
            self.paired_table = None
        if hasattr(self, 'no_paired_label'):
            self.layout.removeWidget(self.no_paired_label)
            self.no_paired_label.deleteLater()
            del self.no_paired_label

    def pair_device(self, mac):
        try:
            subprocess.run(["bluetoothctl", "pair", mac], capture_output=True, timeout=10)
            self.clear_discovered_table()
            self.refresh_paired()
        except Exception:
            pass

    def toggle_connection(self, mac):
        try:
            connected_macs = set(self.get_connected_macs())
            if mac in connected_macs:
                subprocess.run(["bluetoothctl", "disconnect", mac], capture_output=True, timeout=5)
            else:
                subprocess.run(["bluetoothctl", "connect", mac], capture_output=True, timeout=5)
            self.refresh_paired()
        except Exception:
            pass

    def forget_device(self, mac):
        try:
            subprocess.run(["bluetoothctl", "remove", mac], capture_output=True, timeout=5)
            self.refresh_paired()
        except Exception:
            pass