from pathlib import Path

from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Extract text from a PDF.

    First attempts normal PDF text extraction using pypdf.
    If a page contains no extractable text, OCR is used.
    """

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        # First attempt: normal PDF text extraction
        text = page.extract_text() or ""

        text = text.strip()

        if text:
            pages.append(
                {
                    "text": text,
                    "source": pdf_path.name,
                    "page": page_number,
                    "extraction_method": "pdf_text",
                }
            )

            continue

        # If no text was found, use OCR
        print(
            f"  No text found on page {page_number}. "
            f"Running OCR..."
        )

        images = convert_from_path(
            str(pdf_path),
            first_page=page_number,
            last_page=page_number,
            dpi=200,
        )

        if not images:
            continue

        image = images[0]

        ocr_text = pytesseract.image_to_string(
            image
        ).strip()

        if ocr_text:

            pages.append(
                {
                    "text": ocr_text,
                    "source": pdf_path.name,
                    "page": page_number,
                    "extraction_method": "ocr",
                }
            )

    return pages


def load_all_pdfs(documents_dir: Path) -> list[dict]:
    """
    Load all PDF files from the documents directory
    and its subdirectories.
    """

    all_pages = []

    print(
        f"Looking for PDFs in: {documents_dir}"
    )

    if not documents_dir.exists():
        raise FileNotFoundError(
            f"Documents directory does not exist: "
            f"{documents_dir}"
        )

    pdf_files = [
        file
        for file in documents_dir.rglob("*")
        if file.is_file()
        and file.suffix.lower() == ".pdf"
    ]

    print(
        f"Found {len(pdf_files)} PDF files."
    )

    for pdf_file in sorted(pdf_files):

        print(
            f"Reading: {pdf_file.name}"
        )

        pages = extract_text_from_pdf(
            pdf_file
        )

        print(
            f"  Extracted {len(pages)} pages."
        )

        all_pages.extend(pages)

    return all_pages