import os
import json
import google.generativeai as genai
import pypdf  # For reading PDF files
import docx   # For reading DOCX files

# --- Configuration and Setup ---

# Initialize the Gemini client
# It automatically picks up the API key from the GEMINI_API_KEY environment variable.
try:
    # IMPORTANT: It is recommended to use environment variables for API keys.
    # For this example, the key is placed directly.
    api_key = "AIzaSyADl9JhrV6eTFRdKlsHEDdVEixJWoahZFU" # os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable or paste it here.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    exit()

# --- Text Extraction Functions (Unchanged) ---

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
        return ""

def read_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX file '{os.path.basename(file_path)}': {e}")
        return ""

def read_txt(file_path: str) -> str:
    """Reads a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT file '{os.path.basename(file_path)}': {e}")
        return ""

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
        return ""
    else:
        print(f"Warning: Unsupported file type '{extension}' for file '{filename}'. Skipping.")
        return ""

# --- Gemini API Interaction (Modified for Batch Processing) ---

def construct_batch_prompt(resumes_data: dict, required_skills: list[str]) -> str:
    """
    Constructs a detailed prompt for the Gemini API to process multiple resumes,
    filter them by skills, and extract data for the matched ones.
    """
    skills_string = ", ".join(required_skills)

    # Combine all resume texts into one block, with clear separators
    combined_resume_text = ""
    for filename, text in resumes_data.items():
        combined_resume_text += f"--- START OF RESUME: {filename} ---\n"
        combined_resume_text += text + "\n"
        combined_resume_text += f"--- END OF RESUME: {filename} ---\n\n"

    # The prompt is carefully structured to guide the model.
    # It first asks the model to filter and then extract.
    prompt = f"""
    You are an expert HR recruitment assistant. Your task is to analyze a batch of resumes, identify candidates who match a specific set of skills, and then extract key information for ONLY the matched candidates in a strict JSON format.

    The required technical skills we are looking for are: {skills_string}.

    Below is a collection of resumes. Each resume is clearly marked with its source filename.
    --- BATCH OF RESUMES START ---
    {combined_resume_text}
    --- BATCH OF RESUMES END ---

    **Your Instructions:**

    1.  **Analyze and Filter:** Carefully read every resume provided in the batch above. Identify which resumes are a strong match for the required skills: "{skills_string}". A strong match means the resume explicitly mentions several of these skills.

    2.  **Extract Information for Matched Resumes ONLY:** For each resume that you identified as a strong match, extract the following information and format it as a JSON object:
        * "source_file": The original filename of the resume (provided in the start/end markers).
        * "name": The full name of the candidate.
        * "contact_number": The primary phone number.
        * "last_3_companies": A list of the last 3 companies the candidate worked for, starting with the most recent. Be careful to include only the company names, not projects inside companies that the candidate worked for. If there are fewer than 3 companies, include as many as available.
        * "top_5_technical_skills": A list of up to 5 technical skills from the resume that are most relevant to our required skills list.
        * "years_of_experience": The total years of experience the candidate has in their field. Calculate this based on the dates mentioned in the resume.
        * "summary": A brief summary of the candidate's professional background and expertise in not more than 100 words.

    **Output Format:**
    Your output MUST be a single, valid JSON array `[]` containing one JSON object for each matched candidate. If no candidates match the required skills, you MUST return an empty array `[]`.
    Do not include any explanations, introductory text, markdown formatting like ```json, or any text outside of the final JSON array.
    If a piece of information cannot be found, use `null` as the value for that key.
    """
    print("Constructed a batch prompt for the Gemini API.")
    return prompt

def parse_resumes_batch(resumes_data: dict, required_skills: list[str]) -> list[dict]:
    """Sends the combined resume text to the Gemini API for batch parsing and filtering."""
    if not resumes_data:
        print("-> No resume content to process.")
        return []

    prompt = construct_batch_prompt(resumes_data, required_skills)
    print("Connecting to Gemini API to process the batch... (This may take a moment)")

    try:
        # Select the model, Gemini 1.5 Flash is good for this task.
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Configure the generation to output JSON
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )

        # Call the API with the single, combined prompt
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # The response text should be a valid JSON string (a list of objects)
        response_content = response.text
        parsed_data = json.loads(response_content)
        return parsed_data
    except json.JSONDecodeError:
        print("\nError: Failed to decode JSON from the API response.")
        print(f"Raw Gemini Response:\n---\n{response.text}\n---")
        return []
    except Exception as e:
        print(f"\nAn error occurred while communicating with the Gemini API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw Gemini Response:\n---\n{response.text}\n---")
        return []

# --- Main Application Logic (Modified for Batch Processing) ---
class ResumeParser:
    def main(self, dir_path: str, query_string: str) -> list[dict]:
        """Main function to run the resume parser application."""
        print("--- AI-Powered Resume Parser (Batch Mode) ---")
        
        resume_dir = dir_path.strip()
        if not os.path.isdir(resume_dir):
            print(f"Error: Directory '{resume_dir}' not found.")
            return []
            
        skills_input = query_string.strip()
        if not skills_input:
            print("Error: You must specify at least one skill.")
            return []
        required_skills = [skill.strip() for skill in skills_input.split(',')]

        supported_extensions = ('.txt', '.pdf', '.docx', '.doc')
        resume_files = [f for f in os.listdir(resume_dir) if f.lower().endswith(supported_extensions)]

        if not resume_files:
            print(f"No supported resumes (.txt, .pdf, .docx) found in '{resume_dir}'.")
            return []

        print(f"\nFound {len(resume_files)} resume(s). Reading content...")
        
        all_resumes_data = {}
        for filename in resume_files:
            file_path = os.path.join(resume_dir, filename)
            resume_text = get_resume_content(file_path)
            if resume_text and resume_text.strip():
                all_resumes_data[filename] = resume_text
                print(f"  - Successfully read '{filename}'")
            else:
                print(f"  - Could not read content from '{filename}'. Skipping.")

        if not all_resumes_data:
            print("\nCould not read any resume content. Exiting.")
            return []

        # The single API call happens here
        matched_candidates = parse_resumes_batch(all_resumes_data, required_skills)

        if matched_candidates:
            print(f"\n\n--- Found {len(matched_candidates)} Matched Candidate(s) ---")
            # Pretty-print the final JSON output
            print(json.dumps(matched_candidates, indent=4))
            return matched_candidates
        else:
            print("\n--- No candidates matched the required skills from the provided resumes. ---")
            return []

# Example of how to run the class
if __name__ == '__main__':
    # Create a 'resumes' directory in the same folder as this script
    # and add your .pdf, .docx, or .txt resume files there.
    
    # Create an instance of the parser
    parser = ResumeParser()
    
    # Specify the directory containing resumes
    resume_directory = "resumes" 
    
    # Specify the skills you're looking for
    required_skills_query = "Python, data analysis, machine learning, SQL"
    
    # Run the main process
    # This will print the results to the console
    parser.main(resume_directory, required_skills_query)
