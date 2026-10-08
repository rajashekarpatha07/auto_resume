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


def build_skills_prompt(
    jd_json: dict,
    skills_info: str,
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
    You are an expert resume writer. Build the SKILLS section of a resume, tailored
    to the target job.

    Rules:
    - Use ONLY skills that appear in the candidate's skills data below. Never add,
      rename, or upgrade a skill the candidate does not list.
    - Group the skills into 3 to 5 clear categories.
    - Put the skills that match the job's required skills first, both within each
      category and across categories.
    - Drop skills that are irrelevant to this job so the section stays focused
      (aim for roughly 12-20 skills total).
    - Keep skill names short and in their common spelling (e.g. "PostgreSQL").

    Target job (structured):
    {jd_json}

    Candidate skills data (JSON):
    {skills_info}
    {feedback_block}
    """


def build_projects_prompt(
    jd_json: dict,
    projects_info: str,
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
    You are an expert resume writer. Build the PROJECTS section of a resume,
    tailored to the target job.

    Strict rules (accuracy matters more than impressiveness):
    - Select only the 2 to 4 projects from the candidate data that best match
      the job. Copy project names exactly. Never invent a project.
    - Use ONLY facts stated in the candidate data. Do NOT invent or estimate
      metrics, percentages, user counts, performance gains, or team sizes.
      If the data has no numbers, write no numbers.
    - tech_stack must only contain technologies listed for that project.
      Do not add a technology just because the job asks for it.
    - Each project gets 2 to 3 bullets. Start each with a strong action verb
      (Built, Designed, Implemented), keep each under about 25 words.
    - Reword for relevance to the job (emphasize matching keywords), but never
      upgrade the scope of the work (e.g. "contributed to" must not become "led").
    - Include a link only if one is present in the data.

    Target job (structured):
    {jd_json}

    Candidate projects data (JSON):
    {projects_info}
    {feedback_block}
    """


def build_education_prompt(
    jd_json: dict,
    education_info: str,
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
    You are an expert resume writer. Build the EDUCATION section of a resume.

    Strict rules (this section is pure fact, so do not embellish):
    - Include every education entry from the candidate data, most recent first.
    - Copy institution names, degrees, years, grades and locations exactly as written.
      Never invent or round a grade, date, or degree name.
    - If a field is missing in the data, leave it null. Do not guess.
    - highlights: include at most 2 items, and only coursework, honors or activities
      that are present in the data AND relevant to the target job. Otherwise leave empty.
    - extracurriculars: include at most 3 items, only if they are present in the
          candidate data AND add value for the target job (teamwork, leadership,
          relevant technical events). Copy the role and activity as written; do not
          upgrade scope (e.g. "member" must not become "president"). If nothing
          qualifies, return an empty list.

    Target job (structured, used only to choose relevant highlights):
    {jd_json}

    Candidate education data (JSON):
    {education_info}
    {feedback_block}
    """


def build_optimization_prompt(
    jd_json: dict,
    summary_draft: dict,
    skills_draft: dict,
    projects_draft: dict,
    education_draft: dict,
    missing_keywords: list,
    knowledge: dict,
    previous_draft: dict | None = None,
    review_feedback: str | None = None,
) -> str:
    feedback_block = ""
    if review_feedback:
        feedback_block = f"""
        The reviewer rejected the previous result. Revise it using this feedback:
        Previous result: {previous_draft}
        Feedback: {review_feedback}
        """

    return f"""
    You are an expert resume strategist doing a final pass on a resume.

    Target job (structured):
    {jd_json}

    Current resume sections (already approved by the candidate):
    Summary: {summary_draft}
    Skills: {skills_draft}
    Projects: {projects_draft}
    Education: {education_draft}

    JD keywords NOT yet visible in the resume: {missing_keywords}

    Full candidate data (the ONLY source of truth):
    {knowledge}

    Tasks:
    1. section_order: order summary, skills, projects, education so the strongest
       match for this job comes first. Include all four exactly once.
    2. skills_to_add: for each missing keyword, add it ONLY if the candidate data
       explicitly lists that skill (or an obvious exact alias). Use the exact
       spelling from the data and an existing category from the skills draft.
       Never add a skill based on the job description alone.
    3. gaps: list JD requirements the candidate data gives no evidence for.
       Do not try to cover them. This is a report for the candidate.
    4. notes: one or two sentences on why you chose this order.

    {feedback_block}
    """
