import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.dtp_engine import DtpEngine, FORMAT_A4_LANDSCAPE, FORMAT_A4_PORTRAIT


class DtpWorker(QThread):
    """Background worker for DTP pre-press processing."""

    log_message = Signal(str)
    finished = Signal(bool, str)

    def __init__(
        self,
        input_path: str,
        output_path: str,
        width_mm: float,
        height_mm: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.input_path = input_path
        self.output_path = output_path
        self.width_mm = width_mm
        self.height_mm = height_mm

    def run(self) -> None:
        def log(message: str) -> None:
            self.log_message.emit(message)

        success, message = DtpEngine.process(
            self.input_path,
            self.output_path,
            self.width_mm,
            self.height_mm,
            log,
        )
        self.finished.emit(success, message)


class DtpOptimizerTab(QWidget):
    """Tab for pre-press PDF scaling, flattening, and CMYK conversion."""

    FORMAT_OPTIONS = [
        "A4 Poziomo (Folder 2xA5) - 297x210 mm",
        "A4 Pionowo - 210x297 mm",
        "Własny format (mm)",
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: DtpWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        # Główny kontener pionowy zakładki
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        header = QLabel("DTP Optimizer - Przygotowanie do druku")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        # --- SEKCJA: PLIK WEJŚCIOWY ---
        input_group = QGroupBox("Plik wejściowy")
        input_group.setMinimumHeight(72)  # Zabezpieczenie gabarytu przed zgnieceniem
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(10)
        
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Wybierz plik PDF...")
        input_layout.addWidget(self.input_path)

        browse_input = QPushButton("Przeglądaj")
        browse_input.clicked.connect(self._browse_input)
        input_layout.addWidget(browse_input)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # --- SEKCJA: FORMAT DOCELOWY ---
        format_group = QGroupBox("Format docelowy")
        format_group.setMinimumHeight(125)  # Pancerne minimum mieszczące combo + wiersz mm
        
        format_layout = QVBoxLayout()
        format_layout.setContentsMargins(12, 10, 12, 10)
        format_layout.setSpacing(12)

        self.format_combo = QComboBox()
        self.format_combo.addItems(self.FORMAT_OPTIONS)
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        self.format_combo.setMinimumHeight(28)
        format_layout.addWidget(self.format_combo)

        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(10)

        width_label = QLabel("Szerokość (mm):")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("np. 210")
        self.width_input.setEnabled(False)
        self.width_input.setMinimumWidth(90)
        self.width_input.setMinimumHeight(28)
        self.width_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        height_label = QLabel("Wysokość (mm):")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("np. 297")
        self.height_input.setEnabled(False)
        self.height_input.setMinimumWidth(90)
        self.height_input.setMinimumHeight(28)
        self.height_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dims_layout.addWidget(width_label)
        dims_layout.addWidget(self.width_input)
        dims_layout.addSpacing(25)
        dims_layout.addWidget(height_label)
        dims_layout.addWidget(self.height_input)
        dims_layout.addStretch()

        format_layout.addLayout(dims_layout)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # --- SEKCJA: PLIK WYJŚCIOWY ---
        output_group = QGroupBox("Plik wyjściowy")
        output_group.setMinimumHeight(72)  # Zabezpieczenie gabarytu przed zgnieceniem
        
        output_layout = QHBoxLayout()
        output_layout.setContentsMargins(12, 10, 12, 10)
        output_layout.setSpacing(10)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Wybierz lokalizację zapisu...")
        output_layout.addWidget(self.output_path)

        browse_output = QPushButton("Zapisz jako")
        browse_output.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_output)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # --- PRZYCISK AKCJI ---
        self.process_button = QPushButton("Konwertuj do CMYK i Skaluj")
        self.process_button.setObjectName("PrimaryAction")
        self.process_button.setMinimumHeight(40)
        self.process_button.clicked.connect(self._start_processing)
        layout.addWidget(self.process_button)

        log_label = QLabel("Konsola operacji:")
        layout.addWidget(log_label)

        # --- KONSOLA LOGÓW ---
        self.log_console = QTextEdit()
        self.log_console.setObjectName("LogConsole")
        self.log_console.setReadOnly(True)
        self.log_console.setMinimumHeight(120)  # Gwarancja widoczności 5 linii tekstu operacyjnego
        layout.addWidget(self.log_console, stretch=1)

    def _on_format_changed(self, index: int) -> None:
        is_custom = index == 2
        self.width_input.setEnabled(is_custom)
        self.height_input.setEnabled(is_custom)

    def _browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if path:
            self.input_path.setText(path)
            self._append_log(f"Wybrano plik wejściowy: {path}")

    def _browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz jako",
            "",
            "PDF Files (*.pdf)",
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self.output_path.setText(path)
            self._append_log(f"Ustawiono plik wyjściowy: {path}")

    def _resolve_dimensions(self) -> tuple[float, float] | None:
        index = self.format_combo.currentIndex()

        if index == 0:
            return FORMAT_A4_LANDSCAPE
        if index == 1:
            return FORMAT_A4_PORTRAIT

        try:
            width_mm = float(self.width_input.text().strip().replace(",", "."))
            height_mm = float(self.height_input.text().strip().replace(",", "."))
        except ValueError:
            self._append_log("BŁĄD WALIDACJI: Wprowadź poprawne wartości szerokości i wysokości (mm).")
            return None

        return width_mm, height_mm

    def _append_log(self, message: str) -> None:
        self.log_console.append(message)

    def _start_processing(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._append_log("Operacja jest już w toku...")
            return

        dimensions = self._resolve_dimensions()
        if dimensions is None:
            return

        width_mm, height_mm = dimensions
        input_path = self.input_path.text().strip()
        output_path = self.output_path.text().strip()

        self.process_button.setEnabled(False)
        self._append_log("--- Rozpoczęcie przetwarzania DTP ---")

        self._worker = DtpWorker(input_path, output_path, width_mm, height_mm, self)
        self._worker.log_message.connect(self._append_log)
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.start()

    def _on_processing_finished(self, success: bool, message: str) -> None:
        self.process_button.setEnabled(True)
        if success:
            self._append_log(f"ZAKOŃCZONO: {message}")
        else:
            self._append_log(f"PRZERWANO: {message}")
        self._append_log("--- Koniec operacji ---")
        self._worker = None