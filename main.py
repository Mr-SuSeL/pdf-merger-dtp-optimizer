import sys

from PySide6.QtWidgets import QApplication

from src.gui.main_window import PdfMergerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfMergerApp()
    window.show()
    sys.exit(app.exec())
