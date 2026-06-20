import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable

import fitz

MM_TO_PT = 72 / 25.4

FORMAT_A4_LANDSCAPE = (297.0, 210.0)
FORMAT_A4_PORTRAIT = (210.0, 297.0)


class DtpEngine:
    """Pre-press pipeline: scale/flatten via PyMuPDF, CMYK conversion via Ghostscript."""

    @staticmethod
    def mm_to_pt(mm: float) -> float:
        return mm * MM_TO_PT

    @staticmethod
    def find_ghostscript() -> str | None:
        for command in ("gswin64c", "gswin32c", "gs"):
            if shutil.which(command):
                return command

        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        for base in (program_files, program_files_x86):
            candidate = os.path.join(base, "gs", "gs10.04.0", "bin", "gswin64c.exe")
            if os.path.isfile(candidate):
                return candidate

        return None

    @classmethod
    def validate_inputs(
        cls,
        input_path: str,
        output_path: str,
        width_mm: float,
        height_mm: float,
    ) -> tuple[bool, str]:
        input_path = input_path.strip()
        output_path = output_path.strip()

        if not input_path:
            return False, "Nie wybrano pliku wejściowego PDF."

        if not os.path.isfile(input_path):
            return False, f"Plik wejściowy nie istnieje: {input_path}"

        if not input_path.lower().endswith(".pdf"):
            return False, "Plik wejściowy musi mieć rozszerzenie .pdf."

        if not output_path:
            return False, "Nie wybrano ścieżki pliku wyjściowego."

        if not output_path.lower().endswith(".pdf"):
            return False, "Plik wyjściowy musi mieć rozszerzenie .pdf."

        output_dir = os.path.dirname(output_path) or "."
        if not os.path.isdir(output_dir):
            return False, f"Folder docelowy nie istnieje: {output_dir}"

        if width_mm <= 0 or height_mm <= 0:
            return False, "Wymiary formatu muszą być większe od zera."

        if cls.find_ghostscript() is None:
            return False, (
                "Nie znaleziono Ghostscript (gswin64c). "
                "Zainstaluj Ghostscript i dodaj go do PATH systemowego."
            )

        return True, ""

    @classmethod
    def scale_and_flatten(
        cls,
        input_path: str,
        temp_path: str,
        width_mm: float,
        height_mm: float,
        log: Callable[[str], None],
    ) -> None:
        width_pt = cls.mm_to_pt(width_mm)
        height_pt = cls.mm_to_pt(height_mm)

        log(
            f"KROK 1: Skalowanie i spłaszczanie "
            f"({width_mm:g} x {height_mm:g} mm -> {width_pt:.2f} x {height_pt:.2f} pt)..."
        )

        source_doc = fitz.open(input_path)
        output_doc = fitz.open()

        try:
            for page_index in range(len(source_doc)):
                target_page = output_doc.new_page(width=width_pt, height=height_pt)
                target_page.show_pdf_page(
                    target_page.rect,
                    source_doc,
                    page_index,
                    keep_proportion=True,
                )
                log(f"  - Przetworzono stronę {page_index + 1}/{len(source_doc)}")

            output_doc.save(temp_path, garbage=4, deflate=True)
            log(f"KROK 1: Zapisano plik tymczasowy: {temp_path}")
        finally:
            output_doc.close()
            source_doc.close()

    @classmethod
    def convert_to_cmyk(
        cls,
        input_path: str,
        output_path: str,
        log: Callable[[str], None],
    ) -> None:
        ghostscript = cls.find_ghostscript()
        if ghostscript is None:
            raise FileNotFoundError("Ghostscript (gswin64c) nie jest dostępny w systemie.")

        log("KROK 2: Konwersja do CMYK przez Ghostscript...")

        command = [
            ghostscript,
            "-sDEVICE=pdfwrite",
            "-sColorConversionStrategy=CMYK",
            "-sColorConversionStrategyForImages=CMYK",
            "-dProcessColorModel=/DeviceCMYK",
            "-dPDFA=2",
            "-dBATCH",
            "-dNOPAUSE",
            f"-sOutputFile={output_path}",
            input_path,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "Nieznany błąd Ghostscript.").strip()
            raise RuntimeError(f"Ghostscript zakończył się błędem (kod {result.returncode}): {details}")

        log(f"KROK 2: Zapisano plik CMYK: {output_path}")

    @classmethod
    def process(
        cls,
        input_path: str,
        output_path: str,
        width_mm: float,
        height_mm: float,
        log: Callable[[str], None],
    ) -> tuple[bool, str]:
        temp_path: str | None = None

        try:
            is_valid, message = cls.validate_inputs(input_path, output_path, width_mm, height_mm)
            if not is_valid:
                log(f"BŁĄD WALIDACJI: {message}")
                return False, message

            log("Walidacja pól zakończona pomyślnie.")
            log(f"Plik wejściowy: {input_path}")
            log(f"Plik wyjściowy: {output_path}")

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_path = temp_file.name

            cls.scale_and_flatten(input_path, temp_path, width_mm, height_mm, log)
            cls.convert_to_cmyk(temp_path, output_path, log)

            log("SUKCES: Dokument gotowy do druku (CMYK, przeskalowany, spłaszczony).")
            return True, "Dokument został pomyślnie przetworzony."

        except Exception as exc:
            log(f"BŁĄD: {exc}")
            return False, str(exc)

        finally:
            if temp_path and os.path.isfile(temp_path):
                try:
                    os.remove(temp_path)
                    log("Sprzątanie: usunięto plik tymczasowy.")
                except OSError as exc:
                    log(f"Ostrzeżenie: nie udało się usunąć pliku tymczasowego: {exc}")
