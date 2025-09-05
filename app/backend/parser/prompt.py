def construct_batch_prompt(resumes_data: dict, required_skills: list[str]) -> str:
    """
    Constructs a detailed prompt for the GenAI API to process multiple resumes,
    filter them by skills, and extract data for the matched ones.
    """
    skills_string = ", ".join(required_skills)

    # Combine all resume texts into one block, with clear separators
    combined_resume_text = ""
    for filename, text in resumes_data.items():
        combined_resume_text += f"--- START OF RESUME: {filename} ---\n{text}\n--- END OF RESUME: {filename} ---\n\n"
    
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

    2.  **Extract Information for Matched Resumes ONLY:** For each resume that you identified as a strong match, extract the following information and format it as a JSON object. Adhere strictly to the data types and formats specified:
        * "source_file": (String) The original filename of the resume (provided in the start/end markers).
        * "name": (String) The full name of the candidate.
        * "contact_number": (String) The primary phone number.
        * "last_3_companies": (Array of Strings) A list of the last 3 companies the candidate worked for, starting with the most recent. Crucially, include only official company names. Exclude project names, client names, or internal divisions within a company. If fewer than 3 companies are clearly stated, include only all available.
        * "top_5_technical_skills": (Array of Strings) A list of up to 5 technical skills explicitly mentioned in the resume that are most directly relevant to the {skills_string} and/or are highly prominent in the candidate's experience.
        * "years_of_experience": (Number) The total calculated professional work experience in years. Calculate this based on the start and end dates of all full-time work experiences listed. Round it to the nearest whole number
        * "match_score": (Number) An intelligent match score from 0-100 based on how well the candidate matches the required skills "{skills_string}". Consider: More weightage on skills and experience in relevant technologies.
        * "score_breakdown": (String) A brief explanation (max 50 words) of why this score was assigned, highlighting the key strengths that contributed to the score.
        * "summary": (String) A concise summary of the candidate's professional background and expertise, and most significant achievements. This must be no more than 200 words.

    **Output Format:**
    Your output MUST be a single, valid JSON array `[]` containing one JSON object for each matched candidate. If no candidates match the required skills, you MUST return an empty array `[]`.
    Do not include any explanations, introductory text, markdown formatting like ```json, or any text outside of the final JSON array.
    If a piece of information cannot be found, use `null` as the value for that key.
    """
    print("📝 Constructed a batch prompt for the GenAI API.")
    return prompt

__all__ = ['construct_batch_prompt']
