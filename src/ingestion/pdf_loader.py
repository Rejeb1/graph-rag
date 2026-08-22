"""Extract plain text from a PDF file, one page at a time.

Text-based PDFs only — scanned/image PDFs have no extractable text layer
and would need OCR (e.g. pytesseract), which this project doesn't include.
"""

from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [text for page in reader.pages if (text := (page.extract_text() or "").strip())]
    if not pages:
        raise ValueError(
            f"{path.name}: no extractable text found — likely a scanned/image PDF, which needs OCR (not supported)."
        )
    return "\n\n".join(pages)
