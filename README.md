# AI Resume Parser

This project is an AI-powered resume parser designed to extract and analyze information from resumes efficiently.

## Features

- Extracts key details such as name, contact information, skills, experience, and education.
- Supports multiple resume formats (PDF, DOCX, etc.).
- Provides structured output for easy integration with other systems.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/your-username/ai-resume-parser.git
    ```
2. Navigate to the project directory:
    ```
    cd ai-resume-parser
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Place resumes in the `resumes` folder.
2. Create Gemini API key at `https://aistudio.google.com/app/apikey`.
3. Update the API key in `config.py` or set in environment variable.
4. Run the frontend and backend server:
    ```
    serve.bat
    ```
5. Access the app at `http://localhost:8080/` in browser.
