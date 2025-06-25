import os

# Add Gemini AI token here or import from env var
GEMINI_KEY = "AIzaSyBpQYrI-P1cdXID3GJY16O0bhXQDuiuzBA" # os.getenv("GEMINI_KEY")
# AIzaSyAburkU174h2nCfBeg0ILJ2S5X3ZWQ6XG0 - IA
# AIzaSyADkpZb8vXBt5XXklTVynvXxkdkNk9nr74 - SD
# AIzaSyBpQYrI-P1cdXID3GJY16O0bhXQDuiuzBA - ST

# Add Gemini AI model name here
GEMINI_MODEL = "gemini-2.5-flash"

PROMPT_V1 = """
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

PROMPT_V2 = """
    You are an expert HR recruitment assistant. Your task is to analyze a batch of resumes, strictly identify candidates who demonstrate a strong alignment with a specific set of required technical skills, and then extract precise, structured information for ONLY the matched candidates in a JSON array.

        **Required Skills**
        The required technical skills for this role are: {skills_string}.

        **Resume Batch**
        Below is a collection of resumes. Each resume is clearly marked with its source filename.
        --- BATCH OF RESUMES START ---
        {combined_resume_text}
        --- BATCH OF RESUMES END ---

        **Instructions**
            1. Analyze and Filter for Strong Matches:
                - Carefully read and analyze every resume provided.
                - Identify resumes that are a strong match for the {skills_string}. A strong match is defined as a resume that explicitly mentions at least 70% of the provided required skills, or demonstrates a clear depth of experience in a core subset (e.g., 3-4 highly relevant skills mentioned multiple times or in key roles).
                -  Exclude resumes that only superficially mention skills or demonstrate a poor fit.

            2. Extract Information for Matched Resumes ONLY:
                - For each resume identified as a strong match, extract the following information.
                - Adhere strictly to the data types and formats specified.
                - If a piece of information is not found or cannot be reliably determined, use null as its value.
                
                - "source_file": (String) The original filename of the resume (provided in the --- BATCH OF RESUMES START/END --- markers).
                - "name": (String) The full, most prominent name of the candidate as it appears on the resume.
                - "contact_number": (String) The primary, explicitly stated phone number.
                - "last_3_companies": (Array of Strings) A list containing the names of the last 3 distinct companies the candidate worked for, ordered from most recent to least recent.
                    - Crucially, include only official company names. Exclude project names, client names, or internal divisions within a company.
                    - If fewer than 3 companies are clearly stated, include all available.
                    - If no companies are listed, use [].
                - "top_5_technical_skills": (Array of Strings) A list of up to 5 technical skills explicitly mentioned in the resume that are most directly relevant to the {skills_string} and/or are highly prominent in the candidate's experience.
                - "years_of_experience": (Number) The total calculated professional work experience in years.
                    - Calculate this based on the start and end dates of all full-time work experiences listed.
                    - Round to one decimal place.
                    - If the current role is ongoing, calculate up to the current date.
                - "summary": (String) A concise summary of the candidate's professional background and expertise.
                    - This must be no more than 100 words.
                    - Focus on their overall career trajectory, key areas of expertise, and most significant achievements, especially as they relate to technical roles.

        **Output Format**
            - Your output MUST be a single, valid JSON array ([]) containing one JSON object for each matched candidate.
            - Do not include any explanations, introductory text, conversational fillers, markdown formatting like ```json, or any text outside of the final JSON array.
            - If no candidates are found to be a strong match based on the defined criteria, you MUST return an empty array [].
    """

PROMPT_V3 = """
    You are an expert HR recruitment assistant. Your task is to analyze a batch of resumes, identify candidates who match a specific set of skills, and then extract key information for ONLY the matched candidates in a strict JSON format.

    The required technical skills we are looking for are: {skills_string}.

    Below is a collection of resumes. Each resume is clearly marked with its source filename.
    --- BATCH OF RESUMES START ---
    {combined_resume_text}
    --- BATCH OF RESUMES END ---

    **Your Instructions:**

    1.  **Analyze and Filter:** Carefully read every resume provided in the batch above. Identify which resumes are a strong match for the required skills: "{skills_string}". A strong match means the resume explicitly mentions several of these skills.

    2.  **Extract Information for Matched Resumes ONLY:** For each resume that you identified as a strong match, extract the following information and format it as a JSON object. Adhere strictly to the data types and formats specified:
        * "source_file": (String) The original filename of the resume (provided in the start/end markers).
        * "name": (String) The full name of the candidate.
        * "contact_number": (String) The primary phone number.
        * "last_3_companies": (Array of Strings) A list of the last 3 companies the candidate worked for, starting with the most recent. Crucially, include only official company names. Exclude project names, client names, or internal divisions within a company. If fewer than 3 companies are clearly stated, include only all available.
        * "top_5_technical_skills": (Array of Strings) A list of up to 5 technical skills explicitly mentioned in the resume that are most directly relevant to the {skills_string} and/or are highly prominent in the candidate's experience.
        * "years_of_experience": (Number) The total calculated professional work experience in years. Calculate this based on the start and end dates of all full-time work experiences listed. Round it to the nearest whole number
        * "summary": (String) A concise summary of the candidate's professional background and expertise, and most significant achievements. This must be no more than 100 words.

    **Output Format:**
    Your output MUST be a single, valid JSON array `[]` containing one JSON object for each matched candidate. If no candidates match the required skills, you MUST return an empty array `[]`.
    Do not include any explanations, introductory text, markdown formatting like ```json, or any text outside of the final JSON array.
    If a piece of information cannot be found, use `null` as the value for that key.
    """