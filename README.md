# PDF to Word Converter

A local desktop app that converts PDF files into editable Word (.docx) documents. Everything runs on your own computer, so your files are never uploaded anywhere.

## Features

- Simple desktop window with a file picker and one-click conversion (light and dark mode follow your system)
- Command-line mode for quick conversions
- Keeps paragraphs, tables, images and layout as closely as possible using `pdf2docx`
- Detects scanned PDFs automatically and runs OCR first (OCRmyPDF + Tesseract)
- Conversion runs in a background thread, so the window never freezes

## Limitations

No PDF-to-Word converter is 100% accurate. A PDF stores text at exact positions on the page, not real paragraphs, columns or tables, so the converter has to infer the structure. Expect very close results on clean, text-based documents. Complex layouts (multi-column pages, overlapping elements, heavy graphics) and scanned files may need some manual cleanup in Word.

## Tech stack

- Python 3.9+
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) for layout analysis and .docx creation
- [PyMuPDF](https://pymupdf.readthedocs.io/) for reading PDFs and detecting scanned pages
- [OCRmyPDF](https://ocrmypdf.readthedocs.io/) + Tesseract for scanned PDFs (optional)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the desktop window

## Project structure

```
pdf2word/
├── converter.py        # the whole app: conversion logic + window + entry point
├── requirements.txt    # Python packages
└── README.md
```

## Setup

### 1. Create and activate a virtual environment

Windows (Git Bash):

```
python -m venv venv
source venv/Scripts/activate
```

Windows (PowerShell):

```
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### 2. Install the packages

```
pip install -r requirements.txt
```

If installing `ocrmypdf` fails, remove that line from `requirements.txt` and install again. It is only needed for scanned PDFs.

### 3. Install OCR tools (only for scanned PDFs)

OCRmyPDF needs Tesseract and Ghostscript installed on your system.

- **Windows:** install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and [Ghostscript](https://ghostscript.com/releases/gsdnld.html), then add both to your PATH.
- **macOS:** `brew install tesseract ghostscript`
- **Linux (Debian/Ubuntu):** `sudo apt install tesseract-ocr ghostscript`

## Usage

Open the desktop window:

```
python converter.py
```

Click **Browse**, choose a PDF, then click **Convert to Word**. The .docx is saved next to the PDF with the same name.

Command line:

```
python converter.py input.pdf
python converter.py input.pdf output.docx
```

## Add a desktop shortcut (Windows)

1. Right-click the Desktop and choose **New > Shortcut**.
2. For the location, enter the full paths to the venv's `pythonw.exe` and to `converter.py`, each in quotes, on one line. Change the folder to match where you saved the project:
   ```
   "C:\Users\YourName\pdf2word\venv\Scripts\pythonw.exe" "C:\Users\YourName\pdf2word\converter.py"
   ```
3. Name it **PDF to Word** and click Finish.
4. Right-click the shortcut, choose **Properties**, and set **Start in** to your project folder.
5. Double-click the shortcut. `pythonw.exe` runs the app without a console window.

If nothing opens, temporarily change `pythonw.exe` to `python.exe` in the shortcut so the error message is visible.

## How it works

1. `is_scanned()` reads the text of the first few pages. If there is almost no real text, the PDF is treated as scanned images.
2. If scanned, `run_ocr()` creates a searchable copy of the PDF in a temporary folder.
3. `convert_pdf_to_docx()` passes the PDF (or the OCR'd copy) to `pdf2docx`, which rebuilds paragraphs, tables and images as a .docx file.
4. `launch_gui()` wraps this in a CustomTkinter window and runs the conversion in a background thread.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `'python' is not recognized` | Reinstall Python and tick "Add python.exe to PATH" |
| `ModuleNotFoundError` | The virtual environment is not active, or VS Code is using a different interpreter |
| Error about OCR or Tesseract | Install Tesseract and Ghostscript and make sure they are on your PATH |
| Shortcut does nothing | Use `python.exe` instead of `pythonw.exe` to see the error |