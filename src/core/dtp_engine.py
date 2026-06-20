import os
from collections.abc import Callable
import fitz  # PyMuPDF
from PIL import Image

MM_TO_PT = 72 / 25.4

FORMAT_A4_LANDSCAPE = (297.0, 210.0)
FORMAT_A4_PORTRAIT = (210.0, 297.0)


class DtpEngine:
    """Pre-press pipeline z stajni B3 Software: Spłaszcza warstwy do twardego

    rastru 300 DPI i konwertuje piksele bezpośrednio do przestrzeni CMYK.
    Eliminuje potrzebę posiadania zewnętrznego Ghostscripta.
    """

    @staticmethod
    def mm_to_pt(mm: float) -> float:
        return mm * MM_TO_PT

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

        return True, ""

    @classmethod
    def process(
        cls,
        input_path: str,
        output_path: str,
        width_mm: float,
        height_mm: float,
        log: Callable[[str], None],
    ) -> tuple[bool, str]:
        try:
            # 1. Walidacja parametrów wejściowych
            is_valid, message = cls.validate_inputs(input_path, output_path, width_mm, height_mm)
            if not is_valid:
                log(f"BŁĄD WALIDACJI: {message}")
                return False, message

            log("B3 DTP Engine: Walidacja parametrów zakończona sukcesem.")
            log(f"Plik źródłowy: {input_path}")
            log(f"Docelowy format: {width_mm:g} x {height_mm:g} mm")

            # 2. Obliczenie docelowych pikseli dla druku 300 DPI
            # Wzór: (mm / 25.4) * 300 DPI
            target_pixel_w = int(round((width_mm / 25.4) * 300))
            target_pixel_h = int(round((height_mm / 25.4) * 300))
            
            log(f"Matryca rastru 300 DPI: {target_pixel_w} x {target_pixel_h} px")

            # 3. Otwarcie dokumentu wektorowego
            source_doc = fitz.open(input_path)
            total_pages = len(source_doc)
            cmyk_images = []

            log(f"Rozpoczynam renderowanie i spłaszczanie {total_pages} stron...")

            # 4. Pętla przetwarzania stron: Wektor -> Raster RGB -> Profil CMYK
            for page_index in range(total_pages):
                page = source_doc[page_index]
                
                # Podbicie rozdzielczości z domyślnych 72 DPI do produkcyjnych 300 DPI (300 / 72)
                zoom_factor = 300 / 72
                matrix = fitz.Matrix(zoom_factor, zoom_factor)
                
                # Renderowanie strony do Pixmapy (alpha=False wymusza białe tło papieru pod druk)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                
                # Załadowanie surowych bajtów do bufora Pillow
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Precyzyjne dopasowanie do wymiarów milimetrowych (LANCZOS dba o krawędzie czcionek)
                if img.width != target_pixel_w or img.height != target_pixel_h:
                    img = img.resize((target_pixel_w, target_pixel_h), Image.Resampling.LANCZOS)
                
                # Konwersja matematyczna kanałów barwnych na maszynowy CMYK
                log(f" -> Konwersja profilu strony {page_index + 1}/{total_pages} do CMYK...")
                cmyk_img = img.convert("CMYK")
                cmyk_images.append(cmyk_img)

            source_doc.close()

            # 5. Zapis struktury obrazów CMYK do jednego, płaskiego pliku PDF
            if cmyk_images:
                log(f"KROK FINALNY: Kompilacja i zapis pliku wyjściowego...")
                cmyk_images[0].save(
                    output_path,
                    "PDF",
                    resolution=300.0,
                    save_all=True,
                    append_images=cmyk_images[1:]
                )
                
                log(f"SUKCES: Zapisano płaski plik CMYK: {output_path}")
                return True, "Dokument został pomyślnie przetworzony do formatu CMYK."
            
            return False, "Nie wygenerowano żadnych stron."

        except Exception as exc:
            log(f"BŁĄD KRYTYCZNY SILNIKA B3: {exc}")
            return False, str(exc)