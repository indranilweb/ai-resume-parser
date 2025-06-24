import os
import json
import google.generativeai as genai
import pypdf  # For reading PDF files
import docx   # For reading DOCX files

# --- Configuration and Setup ---

# Initialize the Gemini client
# It automatically picks up the API key from the GEMINI_API_KEY environment variable.
try:
    # Load the API key from the environment variable
    api_key = "AIzaSyADl9JhrV6eTFRdKlsHEDdVEixJWoahZFU" # os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    print("Please make sure your GEMINI_API_KEY environment variable is set correctly.")
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

# --- Gemini API Interaction ---

def construct_prompt(resume_text: str, required_skills: list[str]) -> str:
    """Constructs the detailed prompt for the Gemini API."""
    skills_string = ", ".join(required_skills)
    # The prompt is carefully structured to guide the model for JSON output.
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
    5.  "years_of_experience": The total years of experience the candidate has in their field.
    6. "summary": A brief summary of the candidate's professional background and expertise in not more than 100 words.

    Your output MUST be a single, valid JSON object. Do not include any explanations, introductory text, or markdown formatting like ```json. If a piece of information cannot be found, use `null` as the value for that key.
    """
    return prompt

def parse_resume(resume_text: str, required_skills: list[str], filename: str) -> dict:
    """Sends the resume text to the Gemini API for parsing and returns the structured data."""
    if not resume_text or not resume_text.strip():
        print(f"-> Could not read content from '{filename}' or file is empty. Skipping.")
        return None

    prompt = construct_prompt(resume_text, required_skills)
    print(f"Connecting to Gemini API and parsing '{filename}'... (This may take a moment)")

    try:
        # Select the model, Gemini 1.5 Flash is fast and capable.
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Configure the generation to output JSON
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )

        # Call the API
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # The response text should be a valid JSON string
        response_content = response.text
        parsed_data = json.loads(response_content)
        return parsed_data
    except Exception as e:
        print(f"\nAn error occurred while communicating with the Gemini API for file '{filename}': {e}")
        # It's helpful to see the raw response if parsing fails
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw Gemini Response: {response.text}")
        return None

# --- Main Application Logic ---
class ResumeParser:
    def main(self, dir_path: str, query_string: str):
        """Main function to run the resume parser application."""
        print("--- AI-Powered Resume Parser (Gemini Edition) ---")
        
        # default_resume_dir = "resumes"
        # resume_dir = input(f"Enter the path to the directory with resumes (or press Enter for '{default_resume_dir}'): ").strip() or default_resume_dir
        resume_dir = dir_path.strip()

        if not os.path.isdir(resume_dir):
            print(f"Error: Directory '{resume_dir}' not found. Please create it and add your resume files.")
            return
            
        # skills_input = input("Enter the technical skills you are looking for (comma-separated): ").strip()
        skills_input = query_string.strip()
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
            # Pretty-print the final JSON output
            print(json.dumps(all_parsed_data, indent=4))

            # Return the parsed data for further processing if needed
            return all_parsed_data
            
            # Optionally, save to a file
            # output_filename = "parsed_resumes.json"
            # with open(output_filename, 'w', encoding='utf-8') as f:
            #     json.dump(all_parsed_data, f, indent=4)
            # print(f"\nResults have been saved to '{output_filename}'")
            # print("----------------------------------")
        else:
            print("\nNo information could be extracted from any of the provided resumes.")

# if __name__ == "__main__":
#     main()
