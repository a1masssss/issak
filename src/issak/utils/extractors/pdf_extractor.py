import pymupdf


def extract_pdf_text(pdf_path: str) -> str:
    doc = pymupdf.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])