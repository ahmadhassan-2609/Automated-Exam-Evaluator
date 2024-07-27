import os
import streamlit as st
from dotenv import load_dotenv 
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO

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

def create_pdf(report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Center", alignment=1))
    styles.add(ParagraphStyle(name="Analysis", spaceBefore=20))

    elements = []

    # Split the report into sections
    report_lines = report.split('\n')

    # Add title
    elements.append(Paragraph(report_lines[1].strip('# '), styles["Title"]))
    elements.append(Spacer(1, 12))

    # Add subject
    subject_line = report_lines[2].strip('### ')
    elements.append(Paragraph(subject_line, styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # Extract and create table
    table_data = []
    table_data = [["Q No.", "Marks", "Comments"]]
    start_index = report_lines.index("| Question | Marks Obtained | Comments |") + 2
    end_index = [i for i, line in enumerate(report_lines) if line.startswith("**Total Score:**")][0]
    
    for line in report_lines[start_index:end_index]:
        if line.strip():
            row = line.split('|')
            if len(row) > 1:
                table_data.append([Paragraph(cell.strip(), styles["Normal"]) for cell in row[1:-1]])

    col_widths = [0.5 * inch, 1 * inch, 4 * inch]  # Adjust column widths as needed
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Add total score
    total_score_line = [line for line in report_lines if line.startswith("**Total Score:**")][0]
    total_score = total_score_line.strip('** ')
    elements.append(Paragraph(total_score, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Add analysis
    analysis_index = report_lines.index(total_score_line) + 1
    analysis_title = report_lines[analysis_index].strip('### ')
    elements.append(Paragraph(analysis_title, styles["Heading2"]))
    
    analysis_text = "\n".join(report_lines[analysis_index + 1:])
    elements.append(Paragraph(analysis_text, styles["Analysis"]))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer




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
                with st.spinner(f"Generating Report Card for {exam_file_name}"):
                    report = evaluate_exam(solved_exam_text, marking_scheme_text)
                    st.markdown(report)

                    # Generate PDF
                    pdf_buffer = create_pdf(report)

                    st.download_button(
                        label="Download Report Card",
                        data=pdf_buffer,
                        file_name=f"{exam_file_name}_report.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()



