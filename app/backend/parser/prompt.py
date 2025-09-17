def construct_batch_prompt(resumes_data: dict, required_skills: list[str]) -> str:
    """
    Constructs a detailed prompt for the GenAI API to process multiple resumes,
    score ALL resumes based on relevance, and extract data for qualified candidates.
    """
    from .config import MIN_MATCH_SCORE
    
    skills_string = ", ".join(required_skills)

    # Combine all resume texts into one block, with clear separators
    combined_resume_text = ""
    for filename, text in resumes_data.items():
        combined_resume_text += f"--- START OF RESUME: {filename} ---\n{text}\n--- END OF RESUME: {filename} ---\n\n"
    
    # Enhanced prompt that scores ALL resumes instead of binary filtering
    prompt = f"""
    You are an expert HR recruitment assistant. Your task is to analyze a batch of resumes and evaluate ALL candidates against the specified requirements. You should extract information for candidates who score {MIN_MATCH_SCORE} or above on a 0-100 scale, ensuring we don't miss potentially good candidates due to strict filtering.

    **Required Skills/Job Requirements:** {skills_string}

    Below is a collection of resumes. Each resume is clearly marked with its source filename.
    --- BATCH OF RESUMES START ---
    {combined_resume_text}
    --- BATCH OF RESUMES END ---

    **Your Instructions:**

    1. **Analyze ALL Resumes:** Carefully read and evaluate EVERY resume provided above against the requirements: "{skills_string}".

    2. **Scoring Criteria (0-100 scale):**
       - **Skills Match (40%):** Explicit mention of required technologies/skills. Consider exact matches (higher weight) and related/similar technologies (moderate weight)
       - **Experience Level (25%):** Years of relevant experience. If job description mentions experience range (e.g., "3-5 years"), score based on how well candidate fits this range
       - **Industry/Domain Relevance (20%):** Experience in similar projects, companies, or domains
       - **Role Seniority (10%):** Leadership, mentoring, or senior positions that indicate growth
       - **Education/Certifications (5%):** Relevant degrees or certifications

    3. **Include candidates with score ≥ {MIN_MATCH_SCORE}:** Extract information for ANY candidate scoring {MIN_MATCH_SCORE} or above. This ensures we capture:
       - Strong matches (80-100): Excellent fit with most requirements
       - Good matches (60-79): Solid candidates with most skills
       - Moderate matches (45-59): Candidates with core skills but some gaps
       - Potential matches ({MIN_MATCH_SCORE}-44): Early career or transitioning candidates with foundational skills

    4. **Extract Information for Qualified Candidates (score ≥ {MIN_MATCH_SCORE}):** For each qualifying resume, extract the following information and format it as a JSON object:
        * "source_file": (String) The original filename of the resume (provided in the start/end markers).
        * "name": (String) The full name of the candidate.
        * "contact_number": (String) The primary phone number.
        * "last_3_companies": (Array of Strings) A list of the last 3 companies the candidate worked for, starting with the most recent. Include only official company names, exclude project names, client names, or internal divisions. If fewer than 3 companies are available, include all available.
        * "top_5_technical_skills": (Array of Strings) A list of up to 5 technical skills explicitly mentioned in the resume that are most relevant to "{skills_string}". Prioritize exact matches, then related technologies.
        * "years_of_experience": (Number) The total calculated professional work experience in years. Calculate based on start and end dates of all full-time work experiences. Round to the nearest whole number.
        * "match_score": (Number) The calculated match score from 0-100 based on the scoring criteria above.
        * "score_breakdown": (String) A clear explanation (max 80 words) of the score calculation, mentioning specific skills found, experience level, and any gaps. Be specific about what contributed to the score.
        * "summary": (String) A concise summary of the candidate's professional background, key expertise, and most significant achievements relevant to the role. Maximum 200 words.

    **Important Guidelines:**
    - **Don't be overly strict:** A candidate doesn't need ALL required skills to be included
    - **Consider skill synonyms:** React.js and ReactJS are the same; Node.js experience may indicate general backend skills
    - **Weight experience appropriately:** A senior developer with 8 years in related tech but missing 1-2 specific tools may still be valuable
    - **Include career changers:** Someone transitioning from related fields with transferable skills should get fair consideration
    - **Fresh graduates:** If they have relevant projects, internships, or education in the required skills, include them with appropriate scoring

    **Output Format:**
    Your output MUST be a single, valid JSON array `[]` containing one JSON object for each candidate scoring {MIN_MATCH_SCORE} or above. 
    Do not include any explanations, introductory text, markdown formatting like ```json, or any text outside of the final JSON array.
    If a piece of information cannot be found, use `null` as the value for that key.
    If no candidates score {MIN_MATCH_SCORE} or above, return an empty array `[]`.
    """
    print(f"📝 Constructed an enhanced scoring-based prompt for the GenAI API (min score: {MIN_MATCH_SCORE}).")
    return prompt

__all__ = ['construct_batch_prompt']
