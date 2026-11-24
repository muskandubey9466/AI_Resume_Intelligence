
from io import BytesIO
from pypdf import PdfReader
from docx import Document


def extract_resume_text(uploaded_file):

    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    try:

        if file_name.endswith(".pdf"):

            pdf = PdfReader(BytesIO(file_bytes))

            text = ""

            for page in pdf.pages:
                text += page.extract_text() or ""

            return text

        elif file_name.endswith(".docx"):

            document = Document(BytesIO(file_bytes))

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

            return text

        elif file_name.endswith(".txt"):

            return file_bytes.decode(
                "utf-8",
                errors="ignore"
            )

        else:
            return ""

    except Exception as e:
        print(f"Resume extraction error: {e}")
        return ""
