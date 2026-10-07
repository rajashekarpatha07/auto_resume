def build_parse_jd_prompt(
    raw_text: str,
    knowledge_json: str | None = None,
) -> str:
    knowledge_context = ""
    if knowledge_json:
        knowledge_context = f"""
        Use candidate knowledge only as context; extract job requirements and details from the job description, not the candidate data.

        Candidate knowledge JSON:
        {knowledge_json}
        """

    return f"""
    You are an expert HR data extractor. Extract all relevant details from the following job description into the requested JSON schema.

    Job Description:
    {raw_text}

    {knowledge_context}
    """


def build_header_prompt(
    jd_json: dict,
    personal_info: str,
    previous_draft: dict | None = None,
    review_feedback: str | None = None,
) -> str:
    feedback_block = ""
    if review_feedback:
        feedback_block = f"""
        The reviewer rejected the previous draft. Revise it using this feedback:
        Previous draft: {previous_draft}
        Feedback: {review_feedback}
        """

    return f"""
    You are an expert resume writer. Create ONLY the resume header (name, headline,
    contact line) for the candidate, tailored to the target job.

    Rules:
    - Use only facts present in the candidate's personal info. Never invent or
      alter contact details, names, or credentials.
    - The headline should mirror the JD's job title and emphasise the candidate's
      genuinely relevant strengths. Keep it under 15 words.

    Target job (structured):
    {jd_json}

    Candidate personal info (JSON):
    {personal_info}
    {feedback_block}
    """


def build_summary_prompt(
    jd_json: dict,
    summary_info: str,
    previous_draft: dict | None = None,
    review_feedback: str | None = None,
) -> str:
    feedback_block = ""
    if review_feedback:
        feedback_block = f"""
        The reviewer rejected the previous draft. Revise it using this feedback:
        Previous draft: {previous_draft}
        Feedback: {review_feedback}
        """

    return f"""
    You are an expert resume writer. Write the PROFESSIONAL SUMMARY section of a resume.

    Rules:
    - Exactly 4 to 5 sentences, about 60-90 words total. No bullet points.
    - Use only facts present in the candidate's summary data below. Do not invent
      skills, employers, years of experience, or achievements.
    - Tailor the emphasis and keywords to the target job, but only where the
      candidate's background genuinely supports it.
    - Write in an implied first person (no "I", no candidate name).

    Target job (structured):
    {jd_json}

    Candidate summary data (JSON):
    {summary_info}
    {feedback_block}
    """
