import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.pdf_engine import PDFEngine


class MergerTab(QWidget):
    """Tab for merging multiple PDF files into one document."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.selected_files: list[str] = []
        self._build_ui()
        self._refresh_file_preview()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(10)

        header = QLabel("PDF Merger - Łącznik Plików")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        select_button = QPushButton("1. WYBIERZ PLIKI PDF (Możesz zaznaczyć wiele)")
        select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_button.clicked.connect(self._browse_input_files)
        layout.addWidget(select_button)

        preview_label = QLabel("Kolejność plików:")
        layout.addWidget(preview_label)

        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.file_preview.setFixedHeight(120)
        layout.addWidget(self.file_preview)

        output_label = QLabel("Gdzie zapisać połączony plik?")
        layout.addWidget(output_label)

        output_row = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        output_row.addWidget(self.output_path)

        output_button = QPushButton("2. WYBIERZ FOLDER ZAPISU")
        output_button.setFixedWidth(180)
        output_button.setCursor(Qt.CursorShape.PointingHandCursor)
        output_button.clicked.connect(self._browse_output)
        output_row.addWidget(output_button)
        layout.addLayout(output_row)

        self.merge_button = QPushButton("POŁĄCZ PLIKI")
        self.merge_button.setObjectName("PrimaryAction")
        self.merge_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.merge_button.clicked.connect(self._merge_pdfs)
        layout.addWidget(self.merge_button)

        self.status_label = QLabel("Oczekiwanie na pliki...")
        self.status_label.setStyleSheet("color: #888890;")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _browse_input_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Wybierz pliki PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if not paths:
            return

        self.selected_files = PDFEngine.sort_file_paths(paths)
        self._refresh_file_preview()
        count = len(self.selected_files)
        self._update_status(f"Wybrano {count} plik(ów). Ustaw folder zapisu i połącz pliki.")

    def _refresh_file_preview(self) -> None:
        if not self.selected_files:
            self.file_preview.setPlainText("Nie wybrano plików...")
            return

        lines = [
            f"{index}. {os.path.basename(path)}"
            for index, path in enumerate(self.selected_files, start=1)
        ]
        self.file_preview.setPlainText("\n".join(lines))

    def _browse_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Wybierz folder zapisu")
        if directory:
            self.output_path.setText(PDFEngine.build_output_path(directory))
            self._update_status("Miejsce zapisu ustawione. Gotowe do połączenia plików.")

    def _update_status(self, message: str, is_error: bool = False, is_success: bool = False) -> None:
        if is_error:
            color = "#ff6b6b"
        elif is_success:
            color = "#2ecc71"
        else:
            color = "#888890"

        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")

    def _merge_pdfs(self) -> None:
        output = self.output_path.text().strip()
        output_dir = os.path.dirname(output)

        self.merge_button.setEnabled(False)
        try:
            self._update_status("Łączenie plików PDF...")
            success, message = PDFEngine.merge_files(self.selected_files, output_dir)
            self._update_status(message, is_error=not success, is_success=success)

            if success and output_dir:
                self.output_path.setText(PDFEngine.build_output_path(output_dir))
        finally:
            self.merge_button.setEnabled(True)
