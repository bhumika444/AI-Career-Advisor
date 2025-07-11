import streamlit as st
from openai import OpenAI
import os
import re
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt

client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name
    if filename.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        return extract_pdf_text("temp.pdf")
    elif filename.endswith(".docx"):
        with open("temp.docx", "wb") as f:
            f.write(uploaded_file.read())
        return docx2txt.process("temp.docx")
    else:
        return ""

def extract_skills(text):
    skills = re.findall(r'\b[A-Za-z\+\.#]{2,}\b', text)
    return list(set([s.lower() for s in skills]))

st.title("🤖 AI Career Advisor")

resume = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste the Job Description")

if resume and job_description:
    text = extract_text_from_file(resume)
    resume_skills = extract_skills(text)
    jd_skills = extract_skills(job_description)

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    match_percent = round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 0

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

        client = OpenAI(api_key=openai.api_key)

    with st.spinner("Generating..."):
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    st.subheader("📄 Cover Letter")
    st.write(response.choices[0].message.content)
