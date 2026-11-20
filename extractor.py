
import re
import fitz
import pytesseract

from PIL import Image
from pathlib import Path


def extract_document_data(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        document = fitz.open(file_path)
        text = ""

        for page in document:
            page_text = page.get_text()

            if page_text.strip():
                text += page_text + "\n"
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )
                text += pytesseract.image_to_string(image)

        document.close()

    elif extension in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    else:
        raise ValueError("Unsupported document format")

    emails = list(set(re.findall(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )))

    phones = list(set(re.findall(
        r'(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)',
        text
    )))

    dates = list(set(re.findall(
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        text
    )))

    return {
        "text": text,
        "emails": emails,
        "phones": phones,
        "dates": dates
    }
