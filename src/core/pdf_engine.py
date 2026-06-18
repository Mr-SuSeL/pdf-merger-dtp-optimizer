import os
import re

from pypdf import PdfMerger


class PDFEngine:
    """Core PDF sorting and merge operations."""

    DEFAULT_OUTPUT_FILENAME = "polaczony_dokument_do_druku.pdf"

    @staticmethod
    def natural_sort_key(path: str) -> list[str | int]:
        name = os.path.basename(path).lower()
        return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]

    @classmethod
    def sort_file_paths(cls, file_paths: list[str]) -> list[str]:
        return sorted(file_paths, key=cls.natural_sort_key)

    @classmethod
    def build_output_path(cls, output_dir: str) -> str:
        return os.path.join(output_dir, cls.DEFAULT_OUTPUT_FILENAME)

    @classmethod
    def merge_files(cls, file_paths: list[str], output_dir: str) -> tuple[bool, str]:
        if len(file_paths) < 2:
            return False, "🔴 Błąd: Wybierz co najmniej 2 pliki do połączenia!"

        output_dir = output_dir.strip()
        if not output_dir:
            return False, "🔴 Błąd: Nie wybrano folderu zapisu!"

        if not os.path.isdir(output_dir):
            return False, "🔴 Błąd: Folder docelowy nie istnieje."

        for path in file_paths:
            if not os.path.isfile(path):
                return False, f"🔴 Błąd: Plik nie istnieje: {os.path.basename(path)}"

        output_path = cls.build_output_path(output_dir)
        sorted_paths = cls.sort_file_paths(file_paths)

        merger = PdfMerger()
        try:
            for path in sorted_paths:
                merger.append(path)
            with open(output_path, "wb") as output_file:
                merger.write(output_file)
            return True, "🟢 Sukces! Plik został zapisany."
        except Exception as exc:
            return False, f"🔴 Błąd: {exc}"
        finally:
            merger.close()
