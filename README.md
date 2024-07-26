# Automated Test Evaluator 📝

An automated tool for evaluating exam papers based on provided marking schemes. This Streamlit application allows users to upload solved exam papers and corresponding marking schemes in PDF format. The tool generates a detailed report card with marks for each question, comments on mistakes, and an overall analysis of student performance.

## Features

- Upload multiple solved exam papers and marking schemes in PDF format.
- Automatically evaluate the exam papers based on the marking schemes.
- Generate a detailed report card including marks and comments.
- Download the generated report card as a Markdown file.

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running pip install -r requirements.txt.
3. Set up your environment variables by creating a .env file and adding your OpenAI API key:

```
OPENAI_API_KEY="your_openai_api_key"

```

1. Run the application using Streamlit:

```
streamlit run app.py.

```
