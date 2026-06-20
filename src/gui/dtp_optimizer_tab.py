import os

from PySide6.QtCore import QThread, Signal
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(10)

        header = QLabel("DTP Optimizer - Przygotowanie do druku")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        input_group = QGroupBox("Plik wejściowy")
        input_layout = QHBoxLayout(input_group)
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Wybierz plik PDF...")
        input_layout.addWidget(self.input_path)

        browse_input = QPushButton("Przeglądaj")
        browse_input.clicked.connect(self._browse_input)
        input_layout.addWidget(browse_input)
        layout.addWidget(input_group)

        format_group = QGroupBox("Format docelowy")
        format_layout = QVBoxLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(self.FORMAT_OPTIONS)
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)

        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Szerokość (mm):"))
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("np. 210")
        self.width_input.setEnabled(False)
        custom_row.addWidget(self.width_input)

        custom_row.addWidget(QLabel("Wysokość (mm):"))
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("np. 297")
        self.height_input.setEnabled(False)
        custom_row.addWidget(self.height_input)
        format_layout.addLayout(custom_row)
        layout.addWidget(format_group)

        output_group = QGroupBox("Plik wyjściowy")
        output_layout = QHBoxLayout(output_group)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Wybierz lokalizację zapisu...")
        output_layout.addWidget(self.output_path)

        browse_output = QPushButton("Zapisz jako")
        browse_output.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_output)
        layout.addWidget(output_group)

        self.process_button = QPushButton("Konwertuj do CMYK i Skaluj")
        self.process_button.setObjectName("PrimaryAction")
        self.process_button.clicked.connect(self._start_processing)
        layout.addWidget(self.process_button)

        log_label = QLabel("Konsola operacji:")
        layout.addWidget(log_label)

        self.log_console = QTextEdit()
        self.log_console.setObjectName("LogConsole")
        self.log_console.setReadOnly(True)
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
