import os
import streamlit as st
from dotenv import load_dotenv 
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def evaluate_exam(solved_exam_text, marking_scheme_text):
    messages = [
    ("system",
        f"""You are a examiner tasked to evaluate the exam paper based on the marking scheme provided.
        Format:
        ## Report Card
        **Marks Obtained:**

        **Evaluation:** """,
    ),
    ("human", f"""Exam Paper:
                {solved_exam_text}

                Marking Scheme:
                {marking_scheme_text}""")]
    
    llm = ChatOpenAI(api_key=openai_api_key,
                     temperature=0,
                     max_retries=2,
                     verbose=False)
    
    response = llm.invoke(messages)

    return response.content


def main():
    st.set_page_config(page_title='Test Evaluator', layout='wide')
    st.title("Automated Test Evaluator 📝")

    st.header("Upload Files")
    solved_exam_file = st.file_uploader("Upload the solved exam paper (PDF)", type="pdf")
    marking_scheme_file = st.file_uploader("Upload the marking scheme (PDF)", type="pdf")

    if solved_exam_file and marking_scheme_file:
        solved_exam_text = read_pdf(solved_exam_file)
        marking_scheme_text = read_pdf(marking_scheme_file)

        if st.button("Evaluate"):
            with st.spinner("Generating Report Card"):
                report = evaluate_exam(solved_exam_text, marking_scheme_text)
                st.markdown(report)

if __name__ == "__main__":
    main()
