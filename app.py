import os
import streamlit as st
from dotenv import load_dotenv 
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key,
                    temperature=0.2,
                    max_retries=2,
                    verbose=True)

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
    
    response = llm.invoke(messages)

    return response.content

def generate_final_report(reports):
    messages = [
        ("system",
         """You are a report generator tasked with compiling individual exam evaluation reports into a comprehensive final report.
         Your goal is to provide a result table with total scores for each subject and an overall analysis of the student's performance.
         
         The final report should include:
         - A result table with subject names, total scores obtained, and other relevant details.
         - An overall analysis based on the individual reports provided.
         
         Use the following format for the final report:
         
         # Report Card

         ### Result Table
         
         | Subject        | Total Marks Obtained |
         |----------------|----------------------|
         | Subject Name 1 | X/Y                  |
         | Subject Name 2 | X/Y                  | 
         
         ### Overall Analysis

         """),
        ("human",
         f"""Here are the individual reports for each exam paper:
         
         {reports}""")
    ]

    response = llm.invoke(messages)

    return response.content

def pdf_generator(final_report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=26,
        spaceAfter=12,
        alignment=1  # Center align
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        spaceAfter=6,
        alignment=0  # Left align
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        spaceAfter=6,
        alignment=4  # Justified
    )

    # Build the document
    content = []

    # Title
    title = Paragraph("Report Card", title_style)
    content.append(title)
    content.append(Spacer(1, 0.2 * inch))

    # Result Table
    result_table_title = Paragraph("Result Table", heading_style)
    content.append(result_table_title)
    content.append(Spacer(1, 0.1 * inch))

    # Process the summary table from final_report
    table_data = []
    lines = final_report.split('\n')
    
    # Flags to track sections
    in_table = False
    in_analysis = False

    for line in lines:
        # Skip lines that are separators or empty
        if '---' in line or len(line.strip()) == 0:
            continue

        if 'Result Table' in line:
            in_table = True
            continue
        elif 'Overall Analysis' in line:
            in_table = False
            in_analysis = True
            continue
        
        if in_table:
            # Split and clean table data
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            table_data.append(row)
        elif in_analysis:
            # Process and add overall analysis section
            analysis_text = line.strip()
    
    # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
    ])
    
    table = Table(table_data, colWidths=[doc.width/len(table_data[0])] * len(table_data[0]))
    table.setStyle(table_style)
    content.append(table)
    content.append(Spacer(1, 0.2 * inch))

    # Add Overall Analysis section
    if in_analysis and analysis_text:
        analysis_title = Paragraph("Overall Analysis", heading_style)
        content.append(analysis_title)
        content.append(Spacer(1, 0.1 * inch))
        
        overall_analysis = Paragraph(analysis_text, body_style)
        content.append(overall_analysis)
    
    # Build PDF
    doc.build(content)
    
    # Return PDF buffer
    buffer.seek(0)
    return buffer.read()

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
        
        if st.button("Evaluate"):
            reports = []
            with st.spinner(f"Generating Report Card"):
                for (exam_file, marking_scheme_file) in zip(exam_files, marking_scheme_files):
                    solved_exam_text = read_pdf(exam_file)
                    marking_scheme_text = read_pdf(marking_scheme_file)

                    exam_file_name = os.path.splitext(exam_file.name)[0]

                    report = evaluate_exam(solved_exam_text, marking_scheme_text)
                    reports.append((exam_file_name, report))
                
                final_report = generate_final_report(reports)
                st.markdown(final_report)
                
                pdf_buffer = pdf_generator(final_report)
                
                st.download_button(
                    label="Download Report",
                    data=pdf_buffer,
                    file_name="report_card.pdf",
                    mime="application/pdf"
                )
        
if __name__ == "__main__":
    main()
