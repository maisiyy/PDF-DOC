"""
Local PDF -> Word (.docx) converter.
 
Usage:
    python converter.py                      -> opens the desktop window
    python converter.py input.pdf            -> creates input.docx next to it
    python converter.py input.pdf out.docx   -> creates out.docx
"""
 
import sys
import tempfile
import threading
from pathlib import Path
 
import fitz  # PyMuPDF: used to check whether the PDF has real text
from pdf2docx import Converter  # does the actual layout analysis + .docx build
 
 
# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
 
def is_scanned(pdf_path, sample_pages=3, min_chars_per_page=25):
    """Return True if the PDF looks like scanned images (almost no real text)."""
    doc = fitz.open(str(pdf_path))
    try:
        pages = min(sample_pages, len(doc))
        if pages == 0:
            return False
        total_chars = sum(len(doc[i].get_text().strip()) for i in range(pages))
        return total_chars < min_chars_per_page * pages
    finally:
        doc.close()
 
 
def run_ocr(pdf_path, work_dir):
    """Add a text layer to a scanned PDF using OCRmyPDF (needs Tesseract installed)."""
    try:
        import ocrmypdf
    except ImportError:
        raise RuntimeError(
            "This PDF looks scanned, so OCR is needed.\n"
            "Install it with:  pip install ocrmypdf\n"
            "and install Tesseract OCR on your system (see README.md)."
        )
    ocr_pdf = Path(work_dir) / (Path(pdf_path).stem + "_ocr.pdf")
    ocrmypdf.ocr(str(pdf_path), str(ocr_pdf), skip_text=True, deskew=True)
    return ocr_pdf
 
 
def convert_pdf_to_docx(pdf_path, docx_path=None, log=print):
    """Convert one PDF to .docx and return the output path."""
    pdf = Path(pdf_path)
    if not pdf.is_file():
        raise FileNotFoundError(f"File not found: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise ValueError("Input must be a .pdf file")
 
    out = Path(docx_path) if docx_path else pdf.with_suffix(".docx")
 
    # TemporaryDirectory is deleted automatically, so OCR leftovers never pile up.
    with tempfile.TemporaryDirectory() as tmp:
        source = pdf
        if is_scanned(pdf):
            log("Scanned PDF detected - running OCR first (this can take a while)...")
            source = run_ocr(pdf, tmp)
 
        log("Converting to Word...")
        converter = Converter(str(source))
        try:
            converter.convert(str(out))  # all pages
        finally:
            converter.close()  # always release the file handle
 
    log(f"Done: {out}")
    return out
 
 
# ---------------------------------------------------------------------------
# Desktop window (CustomTkinter - a modern-looking layer on top of Tkinter)
# ---------------------------------------------------------------------------
 
def launch_gui():
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
 
    ctk.set_appearance_mode("system")  # follows your Windows light/dark setting
    ctk.set_default_color_theme("blue")
 
    root = ctk.CTk()
    root.title("PDF to Word Converter")
    root.geometry("560x400")
    root.resizable(False, False)
 
    pdf_var = ctk.StringVar()
    status_var = ctk.StringVar(value="Choose a PDF to begin.")
 
    def browse():
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            pdf_var.set(path)
            status_var.set("Ready.")
 
    def set_status(message):
        # Tkinter is not thread-safe, so updates from the worker go through root.after.
        root.after(0, status_var.set, message)
 
    def finish(error=None, out=None):
        progress.stop()
        progress.configure(mode="determinate")
        progress.set(0 if error else 1)  # empty bar on failure, full bar on success
        convert_btn.configure(state="normal")
        if error:
            status_var.set("Failed.")
            messagebox.showerror("Conversion failed", str(error))
        else:
            status_var.set(f"Saved: {out}")
            messagebox.showinfo("Done", f"Saved to:\n{out}")
 
    def worker(pdf_path):
        try:
            out = convert_pdf_to_docx(pdf_path, log=set_status)
            root.after(0, finish, None, out)
        except Exception as exc:
            root.after(0, finish, exc, None)
 
    def start():
        pdf_path = pdf_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No file", "Please choose a PDF first.")
            return
        convert_btn.configure(state="disabled")
        progress.configure(mode="indeterminate")
        progress.start()
        # Run in a thread so the window doesn't freeze during conversion.
        threading.Thread(target=worker, args=(pdf_path,), daemon=True).start()
 
    # --- Header ---
    ctk.CTkLabel(
        root, text="PDF to Word", font=ctk.CTkFont(size=28, weight="bold")
    ).pack(pady=(28, 2))
    ctk.CTkLabel(
        root, text="Convert PDF files into editable Word documents", text_color="gray"
    ).pack()
 
    # --- File picker card ---
    card = ctk.CTkFrame(root, corner_radius=12)
    card.pack(fill="x", padx=32, pady=24)
 
    ctk.CTkLabel(card, text="PDF file", anchor="w").pack(fill="x", padx=16, pady=(14, 4))
 
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0, 16))
    ctk.CTkEntry(row, textvariable=pdf_var, height=36).pack(
        side="left", fill="x", expand=True
    )
    ctk.CTkButton(row, text="Browse", width=90, height=36, command=browse).pack(
        side="left", padx=(10, 0)
    )
 
    # --- Convert button, progress bar, status ---
    convert_btn = ctk.CTkButton(
        root,
        text="Convert to Word",
        height=44,
        font=ctk.CTkFont(size=15, weight="bold"),
        command=start,
    )
    convert_btn.pack(fill="x", padx=32)
 
    progress = ctk.CTkProgressBar(root)
    progress.set(0)
    progress.pack(fill="x", padx=32, pady=(20, 8))
 
    ctk.CTkLabel(
        root, textvariable=status_var, wraplength=480, text_color="gray"
    ).pack()
 
    root.mainloop()
 
 
# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
 
def main():
    args = sys.argv[1:]
    if not args:
        launch_gui()
        return
    try:
        convert_pdf_to_docx(args[0], args[1] if len(args) > 1 else None)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()
 