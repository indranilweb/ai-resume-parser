import os
import json
from openai import OpenAI
import pypdf  # For reading PDF files
import docx   # For reading DOCX files

# --- Configuration and Setup ---

# Initialize the OpenAI client
# It automatically picks up the API key from the OPENAI_API_KEY environment variable.
try:
    OPENAI_API_KEY = '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'
    client = OpenAI(api_key = OPENAI_API_KEY)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure your OPENAI_API_KEY environment variable is set correctly.")
    exit()

# --- Text Extraction Functions ---

def read_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF file '{os.path.basename(file_path)}': {e}")
        return None

def read_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX file '{os.path.basename(file_path)}': {e}")
        return None

def read_txt(file_path: str) -> str:
    """Reads a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT file '{os.path.basename(file_path)}': {e}")
        return None

def get_resume_content(file_path: str) -> str:
    """
    Reads the content of a resume file by dispatching to the correct reader
    based on the file extension.
    """
    filename = os.path.basename(file_path)
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    if extension == '.txt':
        return read_txt(file_path)
    elif extension == '.pdf':
        return read_pdf(file_path)
    elif extension == '.docx':
        return read_docx(file_path)
    elif extension == '.doc':
        print(f"Warning: .doc files are not directly supported. Please convert '{filename}' to .docx or .pdf.")
        return None
    else:
        print(f"Warning: Unsupported file type '{extension}' for file '{filename}'. Skipping.")
        return None

# --- OpenAI API Interaction ---

def construct_prompt(resume_text: str, required_skills: list[str]) -> str:
    """Constructs the detailed prompt for the OpenAI API."""
    skills_string = ", ".join(required_skills)
    prompt = f"""
    You are an expert HR recruitment assistant. Your task is to parse the provided resume text and extract specific information in a strict JSON format.

    The required technical skills we are looking for are: {skills_string}.

    Please analyze the following resume text:
    --- START OF RESUME ---
    {resume_text}
    --- END OF RESUME ---

    From the text above, extract the following information:
    1.  "name": The full name of the candidate.
    2.  "contact_number": The primary phone number.
    3.  "last_3_companies": A list of the last 3 companies the candidate worked for, starting with the most recent.
    4.  "top_5_technical_skills": A list of the top 5 most relevant technical skills from the resume. These skills should be directly from or closely related to the list of required skills I provided ({skills_string}).

    Your output MUST be a single, valid JSON object. Do not include any explanations or introductory text. If a piece of information cannot be found, use `null` as the value for that key.
    """
    return prompt

def parse_resume(resume_text: str, required_skills: list[str], filename: str) -> dict:
    """Sends the resume text to OpenAI for parsing and returns the structured data."""
    if not resume_text or not resume_text.strip():
        print(f"-> Could not read content from '{filename}' or file is empty. Skipping.")
        return None

    prompt = construct_prompt(resume_text, required_skills)
    print(f"Connecting to OpenAI and parsing '{filename}'... (This may take a moment)")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert resume parser that only returns JSON objects."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        response_content = response.choices[0].message.content
        parsed_data = json.loads(response_content)
        return parsed_data
    except Exception as e:
        print(f"\nAn error occurred while communicating with OpenAI for file '{filename}': {e}")
        return None

# --- Main Application Logic ---

def main():
    """Main function to run the resume parser application."""
    print("--- AI-Powered Resume Parser ---")
    
    default_resume_dir = "resumes"
    resume_dir = input(f"Enter the path to the directory with resumes (or press Enter for '{default_resume_dir}'): ").strip() or default_resume_dir

    if not os.path.isdir(resume_dir):
        print(f"Error: Directory '{resume_dir}' not found. Please create it and add your resume files.")
        return
        
    skills_input = input("Enter the technical skills you are looking for (comma-separated): ").strip()
    if not skills_input:
        print("Error: You must specify at least one skill.")
        return
    required_skills = [skill.strip() for skill in skills_input.split(',')]

    supported_extensions = ('.txt', '.pdf', '.docx', '.doc')
    resume_files = [f for f in os.listdir(resume_dir) if f.lower().endswith(supported_extensions)]

    if not resume_files:
        print(f"No supported resumes (.txt, .pdf, .docx) found in '{resume_dir}'.")
        return

    print(f"\nFound {len(resume_files)} resume(s) to process.")
    all_parsed_data = []

    for filename in resume_files:
        print(f"\n--- Processing: {filename} ---")
        file_path = os.path.join(resume_dir, filename)
        
        resume_text = get_resume_content(file_path)

        if resume_text:
            extracted_data = parse_resume(resume_text, required_skills, filename)
            if extracted_data:
                print(f"Successfully extracted information from {filename}.")
                extracted_data['source_file'] = filename
                all_parsed_data.append(extracted_data)
        else:
            # Error/warning messages are handled inside get_resume_content
            print(f"-> Skipped {filename} due to reading error or unsupported format.")

    if all_parsed_data:
        print("\n\n--- All Parsed Resume Data ---")
        print(json.dumps(all_parsed_data, indent=4))
        print("\n----------------------------------")
    else:
        print("\nNo information could be extracted from any of the provided resumes.")

if __name__ == "__main__":
    main()
