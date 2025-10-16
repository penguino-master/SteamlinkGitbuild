from PyQt6.QtWidgets import QApplication
import sys
from gui_mainmenu import SteamlinkGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Global dark theme stylesheet
    app.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;   /* Dark grey background */
            color: white;               /* Default text color */
            font-size: 18px;
        }
        QLabel {
            color: white;
        }
        QPushButton {
            background-color: #2c2f33;
            border-radius: 8px;
            padding: 8px 16px;
            color: white;
        }
        QPushButton:hover {
            background-color: #3a3d41;
        }
        QPushButton:pressed {
            background-color: #505357;
        }
        QProgressBar {
            border: 2px solid #444;
            border-radius: 10px;
            background-color: #2c2f33;
            text-align: center;
            height: 25px;
            font-size: 16px;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #7289da;  /* Blue fill */
            border-radius: 8px;
        }
        QTableWidget {
            background-color: #2c2f33;
            gridline-color: #444;
            color: white;
        }
        QHeaderView::section {
            background-color: #3a3d41;
            color: white;
            padding: 4px;
            border: none;
        }
        QComboBox {
            background-color: #2c2f33;
            color: white;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 4px 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #2c2f33;
            color: white;
            selection-background-color: #7289da;
        }
        /* Ensure grid layouts and tiles inherit dark background */
        QGridLayout {
            background-color: #1e1e1e;
        }
    """)

    gui = SteamlinkGUI()
    gui.showFullScreen()
    sys.exit(app.exec())