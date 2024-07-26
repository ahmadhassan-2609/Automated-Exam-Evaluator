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
            f"""You are an examiner tasked with evaluating an exam paper. Follow the evaluation rubric below to ensure consistency:
            - Award marks based on the completeness and correctness of the answer.
            - Provide comments only if there are mistakes or missing information. Comment should tell the mistake
            - Use the following format for the report card:
            
            # Report Card
            ### Subject: 

            | Question | Marks Obtained | Comments |
            |----------|----------------|----------|
            | 1        | X/Y            | Comment  |
            | 2        | X/Y            | Comment  |

            **Total Score:** X/Y

            ### Analysis
            - Overall performance:
            - Areas for Improvement:

            Be strict and consistent in applying the rubric to each answer.
            """,
            ),
            ("human",
            f"""Exam Paper:
                {solved_exam_text}

                Marking Scheme:
                {marking_scheme_text}""")
            ]

    llm = ChatOpenAI(api_key=openai_api_key,
                     temperature=0.2,
                     max_retries=2,
                     verbose=True)
    
    response = llm.invoke(messages)

    return response.content


def main():
    st.set_page_config(page_title='Test Evaluator', layout='wide')
    st.title("Automated Test Evaluator 📝")
    st.write(
        """
        This tool helps you evaluate exam papers quickly and efficiently.
        Simply upload your solved exam papers and corresponding marking schemes in PDF format.
        The evaluator will generate a detailed report card, providing marks for each question and comments on any mistakes.
        An overall analysis of the student's performance will also be included.
        """
    )
    
    st.header("Upload files")
    exam_files = st.file_uploader("Solved exam papers", type="pdf", accept_multiple_files=True)
    marking_scheme_files = st.file_uploader("Solved marking schemes", type="pdf", accept_multiple_files=True)

    if exam_files and marking_scheme_files:
        if len(exam_files) != len(marking_scheme_files):
            st.error("Please upload an equal number of exam papers and marking schemes.")
            return

        for (exam_file, marking_scheme_file) in zip(exam_files, marking_scheme_files):
            solved_exam_text = read_pdf(exam_file)
            marking_scheme_text = read_pdf(marking_scheme_file)

            exam_file_name = os.path.splitext(exam_file.name)[0]

            if st.button(f"Evaluate {exam_file_name}"):
                with st.spinner(f"Generating Report Card for {exam_file.name}"):
                    report = evaluate_exam(solved_exam_text, marking_scheme_text)
                    st.markdown(report)

                    st.download_button(
                        label="Download Report Card",
                        data=report,
                        file_name=f"{exam_file_name}_report.md",
                        mime="text/markdown"
                    )

if __name__ == "__main__":
    main()
