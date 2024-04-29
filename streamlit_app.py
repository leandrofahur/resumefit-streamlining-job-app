import openai
import streamlit as st
import PyPDF2
from io import BytesIO
import docx

def extract_text_from_pdf(file):
    with BytesIO(file.getvalue()) as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = [page.extract_text() for page in reader.pages]
        return "".join(text) if text else ""

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

# Streamlit UI components for API key input:
api_key = st.text_input("Enter your OpenAI API Key:", type="password")
client = openai.OpenAI(api_key=api_key)

if api_key:
    openai.api_key = api_key

    def compare_resume_to_job_description(resume_text, job_description_text):
        messages = [
        {"role": "system", "content": "You are a recruitment assistant."},
        {"role": "user", "content": f"""
            Given the following resume:
            {resume_text}
            And the following job description:
            {job_description_text}

            Identify the skills and qualifications from both.
            Then, compare them to determine any skill gaps and estimate how qualified the individual is for the job, providing a percentage.
            """
        }
        ]

        # Using the client to make the API call with streaming
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content

    st.title('ResumeFit: Compare Your Resume to Job Descriptions')
    
    # resume_text = st.text_area("Paste Your Resume Here")
    uploaded_file = st.file_uploader("Upload Your Resume", type=['pdf', 'txt', 'docx'])
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "text/plain":
            resume_text = str(uploaded_file.read(), 'utf-8')
    else:
        resume_text = st.text_area("Or paste your resume here")
    
    job_description_text = st.text_area("Paste the Job Description Here")

    submit_button = st.button('Compare')
    if submit_button and resume_text and job_description_text:
        comparison_result = compare_resume_to_job_description(resume_text, job_description_text)
        st.markdown("### Comparison Results")
        st.write(comparison_result)
else:
    st.warning("Please enter your API key to proceed.")