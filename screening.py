
import json
import re

from gemini_service import generate_ai_response


def extract_json(text):

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return json.loads(text)


def screen_resume(resume_text, job_description):

    prompt = f"""
You are an expert recruitment and resume screening assistant.

Evaluate the candidate resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON in the following format:

{{
    "candidate_name": "Candidate name or Not Found",
    "email": "Email or Not Found",
    "phone": "Phone or Not Found",
    "current_role": "Candidate's profile",
    "overall_match_score": 0,
    "ats_score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "experience_summary": "Summary",
    "education_summary": "Summary",
    "strengths": [],
    "improvement_areas": [],
    "recommendation": "Strong Match / Moderate Match / Low Match",
    "reason": "Detailed explanation"
}}

IMPORTANT:
1. Scores must be between 0 and 100.
2. Do not invent candidate information.
3. Consider only evidence present in the resume.
4. Missing information must be marked Not Found.
5. Explain skill mismatches honestly.
6. Do not consider gender, age, religion,
   caste, photograph, or other protected characteristics.
7. Do not automatically reject a candidate.
8. Recommendation must be based on job-related evidence.
"""

    response = generate_ai_response(prompt)

    return extract_json(response)
