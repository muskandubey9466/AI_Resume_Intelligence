
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)
from reportlab.lib.units import inch

from gemini_service import generate_ai_response


def generate_resume_content(details):

    prompt = f"""
Create a professional, ATS-friendly resume.

Use the following candidate information:

{details}

Rules:
1. Use professional language.
2. Create a strong professional summary.
3. Organize skills into relevant categories.
4. Use clear section headings.
5. Use bullet points for experience and projects.
6. Do not invent qualifications or experience.
7. Do not add fake achievements or metrics.
8. Keep the resume concise and factual.
9. Return clean Markdown only.

Suggested sections:
NAME
CONTACT
PROFESSIONAL SUMMARY
EDUCATION
TECHNICAL SKILLS
EXPERIENCE
PROJECTS
CERTIFICATIONS
ACHIEVEMENTS
"""

    return generate_ai_response(prompt)


def create_resume_pdf(resume_text):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ResumeName",
            parent=styles["Title"],
            fontSize=19,
            leading=23,
            textColor=colors.HexColor("#1D4ED8"),
            alignment=TA_CENTER,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeHeading",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1D4ED8"),
            spaceBefore=10,
            spaceAfter=5
        )
    )

    story = []

    for line in resume_text.splitlines():

        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        clean_line = (
            line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        if line.startswith("# "):

            story.append(
                Paragraph(
                    clean_line[2:],
                    styles["ResumeName"]
                )
            )

        elif line.startswith("## ") or (
            line.isupper() and len(line) < 45
        ):

            heading = clean_line.replace("#", "")

            story.append(
                Paragraph(
                    heading,
                    styles["ResumeHeading"]
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.lightgrey
                )
            )

        elif line.startswith(("- ", "* ")):

            story.append(
                Paragraph(
                    "&#8226; " + clean_line[2:],
                    styles["BodyText"]
                )
            )

        else:

            story.append(
                Paragraph(
                    clean_line,
                    styles["BodyText"]
                )
            )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()
