
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from io import BytesIO

from config import APP_NAME, APP_SUBTITLE, PAGE_ICON
from resume_parser import extract_resume_text
from screening import screen_resume
from resume_generator import (
    generate_resume_content,
    create_resume_pdf
)

def excel_export(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Screening Results"
        )

    return output.getvalue()



# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

.main {
    background-color: #F8FAFC;
}

.block-container {
    padding-top: 2rem;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #1E3A8A;
}

.subtitle {
    color: #64748B;
    font-size: 15px;
}

div.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# SESSION STATE
# =====================================

if "screening_results" not in st.session_state:
    st.session_state.screening_results = []

if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = None


# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("📄 AI Resume Intelligence")

st.sidebar.caption("Powered by Google Gemini")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Resume Screening",
        "Resume Generator",
        "Screening Reports"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "AI-powered resume analysis and "
    "professional resume creation."
)

if "home_navigation" in st.session_state:

    page = st.session_state.home_navigation

    del st.session_state.home_navigation



# =====================================
# HOME PAGE
# =====================================

if page == "Home":

    st.markdown(
        f'<div class="main-title">{APP_NAME}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">{APP_SUBTITLE}</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🔍 Resume Screening")

        st.write(
            "Analyze candidate resumes against "
            "job descriptions using AI."
        )

        st.write("""
        - ATS compatibility score
        - Job description matching
        - Matched and missing skills
        - Candidate strengths
        - Interview recommendations
        """)

        if st.button(
            "Start Resume Screening",
            key="home_screen"
        ):

            st.session_state.home_navigation = (
                "Resume Screening"
            )
            st.rerun()

    with col2:

        st.markdown("### 📝 Resume Generator")

        st.write(
            "Create professional and ATS-friendly "
            "resumes using AI."
        )

        st.write("""
        - Professional summary
        - Education and skills
        - Work experience
        - Projects and certifications
        - Downloadable PDF resume
        """)

        if st.button(
            "Create My Resume",
            key="home_generator"
        ):

            st.session_state.home_navigation = (
                "Resume Generator"
            )
            st.rerun()

    st.divider()

    st.subheader("How It Works")

    c1, c2, c3 = st.columns(3)

    c1.metric("Module 01", "Screening")
    c2.metric("Module 02", "Generation")
    c3.metric("Technology", "Gemini AI")


# =====================================
# RESUME SCREENING
# =====================================

elif page == "Resume Screening":

    st.title("🔍 AI Resume Screening")

    st.caption(
        "Upload candidate resumes and compare "
        "them with your job description."
    )

    st.subheader("1. Job Description")

    job_description = st.text_area(
        "Enter Job Description",
        height=200,
        placeholder=(
            "Enter job title, responsibilities, "
            "required skills and qualifications..."
        )
    )

    st.divider()

    st.subheader("2. Upload Candidate Resumes")

    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    st.subheader("3. Bulk Candidate Data (Optional)")

    bulk_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["xlsx", "csv"],
        accept_multiple_files=False
    )

    if bulk_file:

        try:

            if bulk_file.name.endswith(".csv"):
                bulk_df = pd.read_csv(bulk_file)

            else:
                bulk_df = pd.read_excel(bulk_file)

            st.write("Uploaded candidate data:")
            st.dataframe(
                bulk_df,
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"Could not read file: {error}"
            )

    st.caption(
        "Excel/CSV is currently used for candidate data "
        "preview. Upload actual resumes above for AI screening."
    )

    if st.button(
        "🚀 Analyze Resumes",
        use_container_width=True
    ):

        if not job_description.strip():

            st.warning(
                "Please enter a Job Description."
            )

        elif not uploaded_files:

            st.warning(
                "Please upload at least one resume."
            )

        else:

            results = []

            progress = st.progress(0)

            status = st.empty()

            total = len(uploaded_files)

            for index, uploaded_file in enumerate(
                uploaded_files
            ):

                try:

                    if uploaded_file.size > 10 * 1024 * 1024:
                        raise ValueError(
                            "File exceeds 10 MB limit."
                        )

                    status.write(
                        f"Analyzing {uploaded_file.name}..."
                    )

                    resume_text = extract_resume_text(
                        uploaded_file
                    )

                    if not resume_text.strip():
                        raise ValueError(
                            "No readable text found. "
                            "This may be a scanned PDF."
                        )

                    analysis = screen_resume(
                        resume_text,
                        job_description
                    )

                    analysis["file_name"] = (
                        uploaded_file.name
                    )

                    results.append(analysis)

                except Exception as error:

                    st.error(
                        f"{uploaded_file.name}: {error}"
                    )

                progress.progress(
                    (index + 1) / total
                )

            st.session_state.screening_results = results

            status.success(
                "Resume screening completed!"
            )

    # RESULTS

    if st.session_state.screening_results:

        st.divider()

        st.subheader("📊 Screening Results")

        results = st.session_state.screening_results

        for result in results:

            with st.expander(
                f"{result.get('candidate_name', 'Candidate')} "
                f"| {result.get('file_name', '')}"
            ):

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Overall Match",
                    f"{result.get('overall_match_score', 0)}%"
                )

                c2.metric(
                    "ATS Score",
                    f"{result.get('ats_score', 0)}%"
                )

                c3.metric(
                    "Recommendation",
                    result.get(
                        "recommendation",
                        "Not Available"
                    )
                )

                st.write(
                    "**Email:**",
                    result.get("email", "Not Found")
                )

                st.write(
                    "**Phone:**",
                    result.get("phone", "Not Found")
                )

                st.write("### Matched Skills")

                st.write(
                    ", ".join(
                        result.get("matched_skills", [])
                    )
                )

                st.write("### Missing Skills")

                st.write(
                    ", ".join(
                        result.get("missing_skills", [])
                    )
                )

                st.write("### Candidate Strengths")

                for item in result.get("strengths", []):
                    st.write(f"• {item}")

                st.write("### Improvement Areas")

                for item in result.get(
                    "improvement_areas", []
                ):
                    st.write(f"• {item}")

                st.write("### Explanation")

                st.write(
                    result.get("reason", "")
                )

        # SUMMARY CHART

        if results:

            chart_data = pd.DataFrame([
                {
                    "Candidate": r.get(
                        "candidate_name", "Unknown"
                    ),
                    "Match Score": r.get(
                        "overall_match_score", 0
                    )
                }
                for r in results
            ])

            fig = px.bar(
                chart_data,
                x="Candidate",
                y="Match Score",
                title="Candidate Job Match Scores",
                range_y=[0, 100]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            export_df = pd.DataFrame(results)

            st.download_button(
                "📥 Download Screening Report (Excel)",
                data=excel_export(export_df),
                file_name="screening_report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )

            st.download_button(
                "📥 Download Screening Report (CSV)",
                data=export_df.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="screening_report.csv",
                mime="text/csv"
            )


# =====================================
# RESUME GENERATOR
# =====================================

elif page == "Resume Generator":

    st.title("📝 AI Resume Generator")

    st.caption(
        "Enter your details to generate "
        "a professional ATS-friendly resume."
    )

    with st.form("resume_form"):

        st.subheader("Personal Information")

        name = st.text_input("Full Name")

        email = st.text_input("Email Address")

        phone = st.text_input("Phone Number")

        location = st.text_input("Location")

        linkedin = st.text_input("LinkedIn URL")

        github = st.text_input("GitHub / Portfolio URL")

        st.divider()

        st.subheader("Career Information")

        job_role = st.text_input(
            "Target Job Role",
            placeholder="e.g. Data Analyst"
        )

        experience_level = st.selectbox(
            "Experience Level",
            [
                "Fresher",
                "Internship Experience",
                "0-2 Years",
                "2-5 Years",
                "5+ Years"
            ]
        )

        summary = st.text_area(
            "Career Objective / About Me",
            height=100
        )

        st.divider()

        st.subheader("Education")

        education = st.text_area(
            "Education Details",
            placeholder=(
                "Degree, College, Year, CGPA/Percentage"
            )
        )

        st.divider()

        st.subheader("Technical & Professional Skills")

        skills = st.text_area(
            "Skills",
            placeholder="Python, SQL, Excel, Power BI..."
        )

        st.divider()

        st.subheader("Experience")

        experience = st.text_area(
            "Work Experience / Internship",
            height=130,
            placeholder=(
                "Company, designation, duration, "
                "responsibilities and achievements"
            )
        )

        st.divider()

        st.subheader("Projects")

        projects = st.text_area(
            "Project Details",
            height=130,
            placeholder=(
                "Project name, technologies, "
                "description and outcomes"
            )
        )

        st.divider()

        st.subheader("Additional Information")

        certifications = st.text_area(
            "Certifications"
        )

        achievements = st.text_area(
            "Achievements"
        )

        languages = st.text_input(
            "Languages Known"
        )

        generate = st.form_submit_button(
            "✨ Generate Professional Resume",
            use_container_width=True
        )

    if generate:

        if not name.strip() or not job_role.strip():

            st.warning(
                "Please enter your name and target job role."
            )

        else:

            details = {
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Location": location,
                "LinkedIn": linkedin,
                "GitHub": github,
                "Target Role": job_role,
                "Experience Level": experience_level,
                "Career Objective": summary,
                "Education": education,
                "Skills": skills,
                "Experience": experience,
                "Projects": projects,
                "Certifications": certifications,
                "Achievements": achievements,
                "Languages": languages
            }

            with st.spinner(
                "Gemini is creating your resume..."
            ):

                try:

                    resume = generate_resume_content(
                        details
                    )

                    st.session_state.generated_resume = resume

                except Exception as error:

                    st.error(str(error))

    if st.session_state.generated_resume:

        st.divider()

        st.subheader("🎉 Your Generated Resume")

        st.markdown(
            st.session_state.generated_resume
        )

        pdf_data = create_resume_pdf(
            st.session_state.generated_resume
        )

        st.download_button(
            "📥 Download Resume as PDF",
            data=pdf_data,
            file_name="Professional_Resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.download_button(
            "📥 Download Resume as TXT",
            data=st.session_state.generated_resume,
            file_name="Professional_Resume.txt",
            mime="text/plain"
        )

        if st.button("🔄 Create Another Resume"):

            st.session_state.generated_resume = None
            st.rerun()


# =====================================
# SCREENING REPORTS
# =====================================

elif page == "Screening Reports":

    st.title("📊 Screening Reports")

    results = st.session_state.screening_results

    if not results:

        st.info(
            "No screening reports available. "
            "First complete Resume Screening."
        )

    else:

        df = pd.DataFrame(results)

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Resumes",
            len(df)
        )

        c2.metric(
            "Average Match Score",
            f"{pd.to_numeric(df['overall_match_score'], errors='coerce').mean():.1f}%"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        st.download_button(
            "Download CSV",
            data=df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="all_screening_reports.csv",
            mime="text/csv"
        )
