import pymupdf


def extract_pdf_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])