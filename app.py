import os
import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

from octoai.client import OctoAI
from octoai.text_gen import ChatMessage

llama_api_key = st.secrets['LLAMA_API_KEY']

client = OctoAI(api_key=llama_api_key) 

def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def evaluate_exam(solved_exam_text, marking_scheme_text):
    completion = client.text_gen.create_chat_completion(
                    max_tokens=131072,
                    messages=[
                        ChatMessage(
                            role="system",
                            content="""You are an examiner tasked with evaluating an exam paper, ensuring safety and responsibility in your assessments. Follow the evaluation rubric below to ensure consistency:
                            - Award marks based on the completeness and correctness of the answer.
                            - Provide comments only if there are mistakes or missing information. Comment should tell the mistake
                            - Use the following format for the report card:
                            
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
                        ChatMessage(
                            role="user",
                            content=f"""Exam Paper:
                                {solved_exam_text}

                                Marking Scheme:
                                {marking_scheme_text}""",
                        )
                    ],
                    model="meta-llama-3.1-405b-instruct",
                    presence_penalty=0,
                    temperature=0,
                )

    return completion.choices[0].message.content

def generate_final_report(reports):
    completion = client.text_gen.create_chat_completion(
                max_tokens=131072,
                messages=[
                    ChatMessage(
                        role="system",
                        content="""You are a safe and responsible report generator tasked with compiling individual exam evaluation reports into a comprehensive final report.
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
                        """,
                    ),
                    ChatMessage(
                        role="user",
                        content=f"""Here are the individual reports for each exam paper:
        
                                {reports}""",
                    )
                ],
                model="meta-llama-3.1-405b-instruct",
                presence_penalty=0,
                temperature=0,
            )

    return completion.choices[0].message.content

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
    analysis_text = ""
 
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
            analysis_text += line.strip() + "<br/>"
    
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
    st.set_page_config(page_title='Test Evaluator',page_icon="📝", layout='wide')

    col1, col2 = st.columns([7,1])  
    with col1:
        st.title("Automated Test Evaluator 📝| Powered by Meta AI")
    with col2:
        st.image("meta-logo.png", width=125)  

    st.write(
        """
        This tool helps you evaluate exam papers quickly and efficiently.
        Simply upload your solved exam papers and corresponding marking schemes in PDF format.
        The evaluator will generate a detailed report card, providing comments on any mistakes and an overall analysis of the student's performance.
        """
    )

    with st.expander("How It Works"):
        st.write(
            """
            The Automated Test Evaluator app uses the latest :blue[Meta-Llama-3.1-405b-Instruct] AI model to evaluate exam papers based on provided marking schemes. Here’s a breakdown of how it works:

            1. **Upload Exam Papers and Marking Schemes**:
                - Upload your solved exam papers and the corresponding marking schemes in PDF format. Make sure both are clear and legible to facilitate accurate text extraction.

            2. **Text Extraction**:
                - The app extracts text from the uploaded PDF files using a PDF reader. This text is used to assess the answers based on the marking schemes.

            3. **Evaluation**:
                - The AI model evaluates each exam paper by comparing it against the marking scheme. It awards marks, provides comments on mistakes, and generates a report card for each paper.

            4. **Report Generation**:
                - After evaluating all the exam papers, the app compiles the individual reports into a comprehensive final report. This report includes a result table with total scores and an overall analysis of the student's performance.

            5. **Downloading Reports**:
                - You can view and download the final report as a PDF file. The report includes exam scores, and an overall analysis.
            """
        )

    with st.expander("Limitations"):
        st.write(
            """
            1. **Accuracy of Evaluation**:
                - The evaluation relies on the text extracted from the PDF files. Any issues with the text extraction, such as poor quality or non-standard fonts, can affect the accuracy of the evaluation.
                - The AI model evaluates based on the provided marking scheme. Variations or discrepancies in the marking scheme format may lead to inaccurate assessments.
            2. **File Formats**:
                - Only PDF files are supported for both solved exam papers and marking schemes. Other file formats will not be accepted.
                - Ensure the PDFs are clear and legible to facilitate accurate text extraction and evaluation.
            3. **Assessment Criteria**:
                - The app evaluates the completeness and correctness of answers strictly based on the marking scheme provided. It does not account for subjective assessments or partial credit unless specified in the marking scheme.
                - Comments provided are based solely on the detected mistakes and missing information as per the marking scheme.
            4. **Token Limits**:
                - The AI model has a token limit for processing text. Extremely lengthy exam papers or marking schemes may exceed this limit, potentially leading to incomplete evaluations.
            5. **User Inputs**:
                - Equal numbers of exam papers and marking schemes must be uploaded to ensure proper evaluation. Mismatched numbers will result in an error.
                - The evaluation process is automated and does not support manual adjustments or corrections to the generated report.
            """
        )

    with st.expander("Download Sample Files"):
        sample_files_dir = 'data/'
        sample_files = os.listdir(sample_files_dir)
        for file in sample_files:
            with open(os.path.join(sample_files_dir, file), 'rb') as f:
                st.download_button(
                    label=f"Download {file}",
                    data=f,
                    file_name=file,
                    mime='application/pdf'
                )

    st.subheader("Upload files")
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

                for exam_file_name, report in reports:
                    st.write("---")
                    st.markdown(report)

                final_report = generate_final_report(reports)
                st.write("---")
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
