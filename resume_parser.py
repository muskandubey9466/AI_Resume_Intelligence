
import fitz
from docx import Document
from io import BytesIO


def extract_pdf_text(file_bytes):

    text = ""

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text() + "\n"

    pdf.close()

    return text.strip()


def extract_docx_text(file_bytes):

    document = Document(BytesIO(file_bytes))

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    for table in document.tables:

        for row in table.rows:

            row_data = [
                cell.text.strip()
                for cell in row.cells
            ]

            text.append(" | ".join(row_data))

    return "\n".join(text)


def extract_resume_text(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    extension = uploaded_file.name.lower().split(".")[-1]

    if extension == "pdf":
        return extract_pdf_text(file_bytes)

    elif extension == "docx":
        return extract_docx_text(file_bytes)

    else:
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )
