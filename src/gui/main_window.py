from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

from src.gui.dtp_optimizer_tab import DtpOptimizerTab
from src.gui.merger_tab import MergerTab
from src.gui.theme import B3_STYLE


class PdfMergerApp(QMainWindow):
    """Main application window with tabbed PDF tools."""

    # Podbijamy domyślne wymiary, zapewniając pełen oddech dla DTP Optimizera
    WINDOW_WIDTH = 720
    WINDOW_HEIGHT = 680

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Merger & DTP")
        
        # Rozbijamy sztywne setFixedSize na elastyczny start + pancerne minimum techniczne.
        # Dzięki temu trzy QGroupBoxy, przycisk i konsola rozwiną się do 100% swoich wymiarów.
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setMinimumSize(680, 620)
        
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
