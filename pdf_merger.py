# Required installations:
# pip install customtkinter "pypdf<5"

import os
import re
from tkinter import filedialog

import customtkinter as ctk
from pypdf import PdfMerger


class AresPdfMergerApp(ctk.CTk):
    """Desktop app for merging multiple PDFs into one print-ready document."""

    DEFAULT_OUTPUT_FILENAME = "polaczony_dokument_do_druku.pdf"
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 450

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Ares PDF Merger - Gotowość do Druku")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.resizable(False, False)
        self._center_window()

        self.selected_files: list[str] = []
        self.output_path = ctk.StringVar()

        self._build_ui()
        self._refresh_file_preview()

    def _center_window(self) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - self.WINDOW_HEIGHT) // 2
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Ares PDF Merger - Łącznik Plików",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.grid(row=0, column=0, padx=24, pady=(20, 14), sticky="w")

        select_button = ctk.CTkButton(
            self,
            text="1. WYBIERZ PLIKI PDF (Możesz zaznaczyć wiele)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._browse_input_files,
        )
        select_button.grid(row=1, column=0, padx=24, pady=(0, 10), sticky="ew")

        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=2, column=0, padx=24, pady=(0, 10), sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Kolejność plików:",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        preview_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.file_preview = ctk.CTkTextbox(
            preview_frame,
            height=120,
            font=ctk.CTkFont(size=13),
            activate_scrollbars=True,
        )
        self.file_preview.grid(row=1, column=0, sticky="nsew")
        self.file_preview.configure(state="disabled")

        output_section = ctk.CTkFrame(self, fg_color="transparent")
        output_section.grid(row=3, column=0, padx=24, pady=(0, 10), sticky="ew")
        output_section.grid_columnconfigure(0, weight=1)

        output_label = ctk.CTkLabel(
            output_section,
            text="Gdzie zapisać połączony plik?",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        output_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        output_entry = ctk.CTkEntry(
            output_section,
            textvariable=self.output_path,
            state="readonly",
            height=34,
        )
        output_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        output_button = ctk.CTkButton(
            output_section,
            text="2. WYBIERZ FOLDER ZAPISU",
            width=180,
            height=34,
            command=self._browse_output,
        )
        output_button.grid(row=1, column=1, sticky="e")

        merge_button = ctk.CTkButton(
            self,
            text="POŁĄCZ PLIKI",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            command=self._merge_pdfs,
        )
        merge_button.grid(row=4, column=0, padx=24, pady=(4, 8), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Oczekiwanie na pliki...",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray70"),
            anchor="w",
        )
        self.status_label.grid(row=5, column=0, padx=24, pady=(0, 4), sticky="sw")

        exit_button = ctk.CTkButton(
            self,
            text="Exit",
            width=80,
            height=26,
            fg_color="#A93226",
            hover_color="#7B241C",
            text_color="white",
            font=ctk.CTkFont(size=12),
            command=self.destroy,
        )
        exit_button.grid(row=6, column=0, padx=20, pady=(10, 15), sticky="e")

    @staticmethod
    def _natural_sort_key(path: str) -> list[str | int]:
        name = os.path.basename(path).lower()
        return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]

    def _browse_input_files(self) -> None:
        paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if not paths:
            return

        self.selected_files = sorted(paths, key=self._natural_sort_key)
        self._refresh_file_preview()
        count = len(self.selected_files)
        self._update_status(f"Wybrano {count} plik(ów). Ustaw folder zapisu i połącz pliki.")

    def _refresh_file_preview(self) -> None:
        self.file_preview.configure(state="normal")
        self.file_preview.delete("1.0", "end")

        if not self.selected_files:
            self.file_preview.insert("1.0", "Nie wybrano plików...")
        else:
            lines = [
                f"{index}. {os.path.basename(path)}"
                for index, path in enumerate(self.selected_files, start=1)
            ]
            self.file_preview.insert("1.0", "\n".join(lines))

        self.file_preview.configure(state="disabled")

    def _browse_output(self) -> None:
        directory = filedialog.askdirectory()
        if directory:
            full_path = os.path.join(directory, self.DEFAULT_OUTPUT_FILENAME)
            self.output_path.set(full_path)
            self._update_status("Miejsce zapisu ustawione. Gotowe do połączenia plików.")

    def _update_status(self, message: str, is_error: bool = False, is_success: bool = False) -> None:
        if is_error:
            color = ("#e74c3c", "#ff6b6b")
        elif is_success:
            color = ("#27ae60", "#2ecc71")
        else:
            color = ("gray50", "gray70")

        self.status_label.configure(text=message, text_color=color)

    def _normalize_output_path(self, path: str) -> str:
        path = path.strip()
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        return path

    def _merge_pdfs(self) -> None:
        if len(self.selected_files) < 2:
            self._update_status("🔴 Błąd: Wybierz co najmniej 2 pliki do połączenia!", is_error=True)
            return

        output = self.output_path.get().strip()
        if not output:
            self._update_status("🔴 Błąd: Nie wybrano folderu zapisu!", is_error=True)
            return

        for path in self.selected_files:
            if not os.path.isfile(path):
                self._update_status(
                    f"🔴 Błąd: Plik nie istnieje: {os.path.basename(path)}",
                    is_error=True,
                )
                return

        output = self._normalize_output_path(output)
        self.output_path.set(output)

        output_dir = os.path.dirname(output)
        if output_dir and not os.path.isdir(output_dir):
            self._update_status("🔴 Błąd: Folder docelowy nie istnieje.", is_error=True)
            return

        merger = PdfMerger()
        try:
            self._update_status("Łączenie plików PDF...")
            for path in self.selected_files:
                merger.append(path)
            with open(output, "wb") as output_file:
                merger.write(output_file)
            self._update_status("🟢 Sukces! Plik został zapisany.", is_success=True)
        except Exception as exc:
            self._update_status(f"🔴 Błąd: {exc}", is_error=True)
        finally:
            merger.close()


if __name__ == "__main__":
    app = AresPdfMergerApp()
    app.mainloop()
