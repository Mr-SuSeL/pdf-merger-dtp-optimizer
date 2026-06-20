from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

from src.gui.dtp_optimizer_tab import DtpOptimizerTab
from src.gui.merger_tab import MergerTab
from src.gui.theme import B3_STYLE


class PdfMergerApp(QMainWindow):
    """Main application window with tabbed PDF tools."""

    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 580

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Merger - Gotowość do Druku")
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setStyleSheet(B3_STYLE)
        self._center_window()
        self._build_ui()

    def _center_window(self) -> None:
        frame = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(8)

        self.tabs = QTabWidget()
        self.tabs.addTab(MergerTab(), "PDF Merger")
        self.tabs.addTab(DtpOptimizerTab(), "DTP Optimizer")
        layout.addWidget(self.tabs)

        footer = QHBoxLayout()
        footer.addStretch()

        exit_button = QPushButton("Exit")
        exit_button.setObjectName("ExitButton")
        exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_button.clicked.connect(self.close)
        footer.addWidget(exit_button)
        layout.addLayout(footer)
