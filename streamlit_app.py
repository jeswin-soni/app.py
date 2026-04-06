import streamlit as st
import pdfplumber
import docx
import requests
import google.generativeai as genai
import os

# --- Configuration ---
st.set_page_config(page_title="Auto AI Job Applier", page_icon="💼", layout="wide")

# Set up your Gemini API Key securely (You will add this in Streamlit secrets later)
API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_LOCAL_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Helper Functions ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def search_jobs(role, location):
    """
    Mock function for job searching. 
    In reality, scraping LinkedIn/Indeed directly usually blocks free servers. 
    It is recommended to use an API like SerpApi (Google Jobs API) here.
    """
    # Example mock data
    st.info("Fetching jobs from Google Jobs / Portals (Mock Data for demonstration)...")
    return [
        {"title": f"Senior {role}", "company": "Tech Corp", "link": "https://techcorp.com/careers", "jd": f"Looking for a {role} with strong problem-solving skills and experience in Python and Cloud."},
        {"title": f"{role} Developer", "company": "Innovate AI", "link": "https://innovateai.com/jobs", "jd": f"Seeking a {role} to build scalable web applications. Must know React and Node.js."}
    ]

def tailor_application(base_resume_text, job_description):
    prompt = f"""
    You are an expert ATS-friendly resume writer. 
    Here is my current resume:
    {base_resume_text}
    
    Here is the Job Description:
    {job_description}
    
    1. Tailor my resume to match the keywords and tone of this job description. Keep it professional and strictly truthful to my original experience, but highlight the most relevant skills. Format it clearly.
    2. Write a compelling, concise cover letter for this specific role.
    
    Output the tailored resume first, followed by a separator '---COVER LETTER---', and then the cover letter.
    """
    response = model.generate_content(prompt)
    return response.text

# --- Main Web App UI ---
st.title("🚀 AI Auto Job Tailor & Search")
st.markdown("Upload your base resume, search for roles, and let AI tailor your application for you.")

# 1. Upload Resume
st.header("1. Upload Base Resume")
uploaded_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

resume_text = ""
if uploaded_file is not None:
    if uploaded_file.name.endswith('.pdf'):
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        resume_text = extract_text_from_docx(uploaded_file)
    st.success("Resume uploaded and parsed successfully!")

# 2. Search Jobs
st.header("2. Search for Jobs")
col1, col2 = st.columns(2)
with col1:
    job_role = st.text_input("Job Role (e.g., Software Engineer)")
with col2:
    job_location = st.text_input("Location (e.g., Remote, New York)")

if st.button("Search Jobs") and job_role:
    jobs = search_jobs(job_role, job_location)
    st.session_state['jobs'] = jobs

# 3. Display Jobs & Auto-Tailor
if 'jobs' in st.session_state:
    st.header("3. Job Matches & Tailoring")
    for idx, job in enumerate(st.session_state['jobs']):
        with st.expander(f"{job['title']} at {job['company']}"):
            st.markdown(f"**Apply Link:** [Click Here]({job['link']})")
            st.markdown(f"**Job Description:** {job['jd']}")
            
            if st.button(f"Tailor CV & Cover Letter for this job", key=f"tailor_{idx}"):
                if not resume_text:
                    st.error("Please upload your base resume first!")
                else:
                    with st.spinner("AI is tailoring your application to be ATS friendly..."):
                        result = tailor_application(resume_text, job['jd'])
                        st.markdown("### 📝 Your Tailored Application")
                        st.write(result)
