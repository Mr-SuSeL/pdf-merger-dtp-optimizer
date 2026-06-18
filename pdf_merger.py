# Required installations:
# pip install customtkinter "pypdf<5"

import os
from tkinter import filedialog

import customtkinter as ctk
from pypdf import PdfMerger


class AresPdfMergerApp(ctk.CTk):
    """Desktop app for merging two single-page PDFs into one double-sided document."""

    DEFAULT_OUTPUT_FILENAME = "polaczony_dokument_do_druku.pdf"

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Ares PDF Merger - Gotowość do Druku")
        self.geometry("600x400")
        self.resizable(False, False)
        self._center_window()

        self.front_path = ctk.StringVar()
        self.back_path = ctk.StringVar()
        self.output_path = ctk.StringVar()

        self._build_ui()

    def _center_window(self) -> None:
        self.update_idletasks()
        width, height = 600, 400
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Łącznik PDF (Format Dwustronny)",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.grid(row=0, column=0, padx=24, pady=(20, 16), sticky="w")

        self._add_file_section(
            row=1,
            label_text="Wybierz plik na PRZÓD dokumentu:",
            path_var=self.front_path,
            browse_command=self._browse_front,
        )
        self._add_file_section(
            row=2,
            label_text="Wybierz plik na TYŁ dokumentu:",
            path_var=self.back_path,
            browse_command=self._browse_back,
        )
        self._add_file_section(
            row=3,
            label_text="Gdzie zapisać połączony plik?",
            path_var=self.output_path,
            browse_command=self._browse_output,
            browse_text="Wybierz miejsce...",
        )

        merge_button = ctk.CTkButton(
            self,
            text="POŁĄCZ PLIKI W JEDEN PDF",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            command=self._merge_pdfs,
        )
        merge_button.grid(row=4, column=0, padx=24, pady=(18, 8), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Oczekiwanie na pliki...",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray70"),
            anchor="w",
        )
        self.status_label.grid(row=5, column=0, padx=24, pady=(0, 16), sticky="sw")

    def _add_file_section(
        self,
        row: int,
        label_text: str,
        path_var: ctk.StringVar,
        browse_command,
        browse_text: str = "Przeglądaj...",
    ) -> None:
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.grid(row=row, column=0, padx=24, pady=(0, 10), sticky="ew")
        section.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            section,
            text=label_text,
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        entry = ctk.CTkEntry(
            section,
            textvariable=path_var,
            state="readonly",
            height=34,
        )
        entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            section,
            text=browse_text,
            width=130,
            height=34,
            command=browse_command,
        )
        browse_btn.grid(row=1, column=1, sticky="e")

    def _browse_front(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.front_path.set(path)
            self._update_status("Wybrano plik przodu. Wybierz plik tyłu i miejsce zapisu.")

    def _browse_back(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.back_path.set(path)
            self._update_status("Wybrano plik tyłu. Ustaw miejsce zapisu i połącz pliki.")

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
        front = self.front_path.get().strip()
        back = self.back_path.get().strip()
        output = self.output_path.get().strip()

        if not front or not back or not output:
            self._update_status("🔴 Błąd: Nie wybrano plików!", is_error=True)
            return

        if not os.path.isfile(front):
            self._update_status("🔴 Błąd: Plik przodu nie istnieje.", is_error=True)
            return

        if not os.path.isfile(back):
            self._update_status("🔴 Błąd: Plik tyłu nie istnieje.", is_error=True)
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
            merger.append(front)
            merger.append(back)
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
