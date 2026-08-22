import pytest

reportlab = pytest.importorskip("reportlab", reason="reportlab only needed to generate the test PDF fixture")
pypdf = pytest.importorskip("pypdf", reason="requires pip install -r requirements-ingestion.txt")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.ingestion.pdf_loader import extract_pdf_text


def _make_pdf(path, lines: list[str]) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    y = 700
    for line in lines:
        c.drawString(72, y, line)
        y -= 20
    c.save()


def test_extracts_text_from_a_real_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_pdf(pdf_path, ["Graph-RAG test document.", "Second line of text."])

    text = extract_pdf_text(pdf_path)

    assert "Graph-RAG test document." in text
    assert "Second line of text." in text


def test_multi_page_pdf_joins_pages(tmp_path):
    pdf_path = tmp_path / "two_page.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(72, 700, "Page one content.")
    c.showPage()
    c.drawString(72, 700, "Page two content.")
    c.save()

    text = extract_pdf_text(pdf_path)

    assert "Page one content." in text
    assert "Page two content." in text


def test_blank_pdf_raises_value_error(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.showPage()
    c.save()

    with pytest.raises(ValueError, match="no extractable text"):
        extract_pdf_text(pdf_path)
