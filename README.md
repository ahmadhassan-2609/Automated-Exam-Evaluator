# Automated Exam Evaluator 📝

This Streamlit application provides an automated way to evaluate exam papers based on provided marking schemes. It generates a comprehensive final report from the evaluations of multiple exam papers and marking schemes, which can be downloaded as a PDF.

## Features

- **Upload Exam Papers and Marking Schemes**: Upload multiple solved exam papers and corresponding marking schemes in PDF format.
- **Automatic Evaluation**: The app evaluates each exam paper according to the marking scheme.
- **Generate Final Report**: A single comprehensive final report is generated, including a result table of all subjects and an overall analysis of student performance.
- **Download PDF**: The final report can be downloaded as a styled PDF.

![frontend](https://github.com/user-attachments/assets/919f83a1-ca47-4e4c-94ab-18872097dd2f)
![frontend_2](https://github.com/user-attachments/assets/273dad7e-00e4-43f6-8437-87dfe11fd0bd)
![report card](https://github.com/user-attachments/assets/2314bda7-33e1-4f2c-aa56-01404211e383)

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running pip install -r requirements.txt.
3. Set up your environment variables by creating a .env file and adding your OpenAI API key:

```
OPENAI_API_KEY="your_openai_api_key"

```

4. Run the application using Streamlit:

```
streamlit run app.py.

```
