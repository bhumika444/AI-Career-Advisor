import streamlit as st
import openai
import re
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = st.secrets["OPENAI_API_KEY"] or os.getenv("OPENAI_API_KEY")

def extract_skills(text):
    skills = re.findall(r'\b[A-Za-z\+\.#]{2,}\b', text)
    return list(set([s.lower() for s in skills]))

st.title("🤖 AI Career Advisor")

resume = st.file_uploader("Upload your Resume (PDF/DOCX)", type=['pdf', 'docx'])
job_description = st.text_area("Paste the Job Description")

if resume and job_description:
    import textract

    text = textract.process(resume).decode("utf-8")
    resume_skills = extract_skills(text)
    jd_skills = extract_skills(job_description)

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    match_percent = round(len(matched) / len(jd_skills) * 100, 2)

    st.subheader("🔍 Skill Match Results")
    st.write(f"✅ **Match:** {match_percent}%")
    st.write(f"✔️ Matched Skills: {matched}")
    st.write(f"❌ Missing Skills: {missing}")

    if st.button("✍️ Generate Cover Letter"):
        prompt = f"""
        Write a short and professional cover letter for a job with the following description:
        {job_description}

        Based on the candidate's resume which includes these skills:
        {resume_skills}

        Focus on highlighting matching skills: {matched}, and express eagerness to learn: {missing}.
        """

        with st.spinner("Generating..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            st.subheader("📄 Cover Letter")
            st.write(response['choices'][0]['message']['content'])
