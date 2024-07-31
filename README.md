# Automated Exam Evaluator 📝

## Introduction

The Automated Exam Evaluator is a tool designed to help you evaluate exam papers quickly and efficiently. This app utilizes the Meta-Llama-3.1-405b-Instruct AI model to assess exam papers based on provided marking schemes, generating detailed report cards and a comprehensive final report.

You can access the deployed app [here](https://automated-exam-evaluator.streamlit.app/)

## How It Works

1. **Upload Exam Papers and Marking Schemes**: Upload solved exam papers and corresponding marking schemes in PDF format.
2. **Text Extraction**: The app extracts text from the PDF files using a PDF reader.
3. **Evaluation**: The AI model evaluates each exam paper, awarding marks and providing comments based on the marking scheme.
4. **Report Generation**: The app compiles individual reports into a final report, including a result table and overall analysis.
5. **Downloading Reports**: You can download the final report as a PDF file.

## Limitations

1. **Accuracy of Evaluation**: Evaluation relies on the quality of text extraction and the provided marking scheme.
2. **File Formats**: Only PDF files are supported.
3. **Assessment Criteria**: Evaluations are strictly based on the marking scheme provided.
4. **Token Limits**: Extremely lengthy documents may exceed the AI model's token limit.
5. **User Inputs**: Equal numbers of exam papers and marking schemes must be uploaded for proper evaluation.

## Installation

1. Clone the repository:
    
    ```
    git clone <repository_url>
    cd <repository_directory>
    ```
    
2. Install the required dependencies:
    
    ```
    pip install -r requirements.txt
    ```
    
3. Set up your Streamlit secrets by creating a `secrets.toml` file with your LLAMA API key:
    
    ```toml
    [secrets]
    LLAMA_API_KEY = "your_llama_api_key"
    ```
    

## Usage

1. Run the Streamlit app:
    
    ```
    streamlit run app.py
    ```
    
2. Open your browser and navigate to the Streamlit app URL.
3. Follow the instructions to upload exam papers and marking schemes.
4. Click "Evaluate" to generate report cards and the final report.
5. Download the generated reports as PDF files.

## Sample Files

Sample files are available for download within the app under the "Download Sample Files" section.
