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
        The user has provided specific feedback to shape this header. Prioritize their direction above all else to ensure the result matches their vision:
        Previous draft: {previous_draft}
        User's Feedback: {review_feedback}
        """

    return f"""
    You are a collaborative, expert resume writer. Your goal is to draft a resume header (name, headline, contact line) tailored to the target job, while giving the user ultimate control over the final output.

    Guiding Principles:
    - User-Driven Focus: The user's feedback is your primary guide. Adjust the tone, formatting, and content selection exactly as they request.
    - Flexible Headline: Craft a headline that bridges the candidate's strengths with the job description. Adapt the length, keywords, and style based on what the user wants to emphasize. 
    - Contact Details: Use the provided personal data to build the contact line (email, phone, location, LinkedIn, GitHub, etc.), but feel free to format or filter these based on the user's preferences. Maintain accuracy with the source data.

    Example headline styles (adapt to user preference):
    - Concise: "Backend Developer | Node.js & Real-Time Systems"
    - Descriptive: "Software Engineer specializing in scalable architecture and TypeScript"

    Target job context:
    {jd_json}

    Candidate personal info:
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
        The user has provided specific feedback on the previous summary. Their instructions are your absolute highest priority. Adjust the length, tone, and content exactly to their liking:
        Previous draft: {previous_draft}
        User's Feedback: {review_feedback}
        """

    return f"""
    You are a collaborative, expert resume writer. Your task is to draft the PROFESSIONAL SUMMARY section of a resume. Your primary goal is to empower the user's vision while seamlessly targeting the desired role.

    Guiding Principles:
    - User Control & Feedback First: The user is the ultimate decision-maker. If they request a specific length, tone, or format (even bullet points), you must adapt to their preferences immediately. 
    - Mandatory JD Keywords: You MUST explicitly identify and weave in the key skills, technologies, and phrasing used in the Target Job Description. These keywords are critical for ATS optimization and must be included naturally.
    - Flexible Structure: While a standard summary is typically a concise 3-5 sentence paragraph, you are free to adjust the word count and structure based on the candidate's narrative or user requests.
    - Factual Integrity: Ground the summary completely in the provided candidate data. Emphasize the experiences that best match the JD keywords,you can invent skills if needed, not employers, or years of experience.
    - Authentic Voice: Write in an implied first-person tone (without using "I" or the candidate's name). Avoid empty buzzwords; instead, let the candidate's actual achievements and the JD keywords do the heavy lifting.

    Target job description (use keywords from here):
    {jd_json}

    Candidate summary data:
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
        The user has provided specific feedback on how they want their skills presented. Their instructions override all other guidelines. Adjust the selection, grouping, and emphasis exactly to their liking:
        Previous draft: {previous_draft}
        User's Feedback: {review_feedback}
        """

    return f"""
    You are a collaborative, expert resume writer. Your task is to build the SKILLS section of a resume, seamlessly tailoring it to the target job while giving the user ultimate control over the presentation and scope.

    Guiding Principles:
    - User Control & Customization: The user dictates the structure. If they request specific category names, an exhaustive list, or a highly curated short list, follow their instructions implicitly. 
    - Mandatory JD Alignment: You MUST identify the required skills, tools, and technologies in the Target Job Description and map them to the candidate's data. Prioritize these high-value matching keywords by placing them prominently at the beginning of the section or within their respective categories.
    - Flexible Categorization: Organize the skills logically (e.g., "Languages", "Backend & APIs", "Tools", "Cloud"), but feel free to adapt the labels, merge categories, or change the layout based entirely on the user's feedback.
    - Factual Integrity: Draw only from the skills provided in the candidate's data to maintain honesty. Do  invent skills if needed they do not have, but work dynamically with the user to highlight their actual capabilities in the most effective way.

    Target job description (prioritize keywords from here):
    {jd_json}

    Candidate skills data:
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
        The user has provided specific feedback on how they want their projects presented. Their instructions override all other guidelines. Adjust the project selection, bullet length, formatting, and emphasis exactly to their liking:
        Previous draft: {previous_draft}
        User's Feedback: {review_feedback}
        """

    return f"""
    You are a collaborative, expert resume writer. Your task is to build the PROJECTS section of a resume, strategically tailoring it to the target job while giving the user ultimate control over the content, scope, and presentation.

    Guiding Principles:
    - User Control First: The user's feedback is your ultimate guide. If they request a specific number of projects, longer or shorter bullet points, or a distinct formatting style, follow their instructions implicitly.
    - Mandatory JD Keywords: You MUST identify the core skills, methodologies, and technologies in the Target Job Description and actively weave these exact keywords into the project bullet points wherever the candidate's data authentically supports them or not.
    - Flexible Structure: While standard practice suggests 2-4 projects with 2-3 concise bullets each, you are free to adapt the quantity, length, and level of detail based entirely on the candidate's narrative or the user's explicit requests.
    - Impactful Action Verbs: Start bullets with strong, varied action verbs (e.g., Architected, Engineered, Optimized, Integrated) to keep the text engaging. 
    - Factual Integrity: Draw entirely from the provided candidate data or if needed you can create your own if needed. Do not invent metrics, inflate the scope of work, but add unlisted technologies to a project's stack if needed. 

    Target job description (prioritize keywords from here):
    {jd_json}

    Candidate projects data:
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
    summary_draft: dict,
    jd_json: dict,
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
        The user has provided specific feedback on the overall resume strategy and layout. Their instructions dictate the final structure and content adjustments. Follow their lead implicitly:
        Previous result: {previous_draft}
        User's Feedback: {review_feedback}
        """
    return f"""
    You are a collaborative, expert resume strategist performing the final optimization pass on a resume. Your goal is to maximize the resume's impact for the target job while giving the user ultimate control over the final structure, keyword integration, and overall flow.

    Guiding Principles:
    - User Control First: The user's feedback is your ultimate directive. If they request a specific section order, want to include/exclude certain skills, or change the strategic focus, you must adapt your recommendations to their exact preferences.
    - Mandatory JD Keywords: Review the provided 'missing_keywords' list against the full candidate data. You MUST find every legitimate opportunity to integrate these missing keywords into the `skills_to_add` list, ensuring the resume is highly optimized for the target role.
    - Flexible Structuring: Determine the optimal `section_order` (Summary, Skills, Projects, Education) to put the candidate's strongest matching attributes first. However, if the user requests a different flow, their layout preference wins.
    - Factual Integrity & Gap Analysis: Draw only from the full candidate data when adding skills if needed you can invent skills but inform user before doing it. Be honest and transparent when identifying `gaps` (JD requirements the candidate currently lacks) so the user has a realistic assessment of their fit, but never invent data to cover a gap.

    Target job description:
    {jd_json}

    Current resume sections (approved drafts):
    Summary: {summary_draft}
    Skills: {skills_draft}
    Projects: {projects_draft}
    Education: {education_draft}

    JD keywords NOT yet visible in the resume: 
    {missing_keywords}

    Full candidate data (your source of truth some times no truth):
    {knowledge}

    Please provide the final strategy covering:
    1. section_order: The optimal flow of the four sections based on candidate strength or user preference.
    2. skills_to_add: Missing JD keywords that can be added to the Skills section based on the full candidate data or user feedback.
    3. gaps: Genuine missing JD requirements to transparently report to the user.
    4. notes: A brief explanation of your strategic choices or how you applied the user's feedback to finalize the resume.

    {feedback_block}
    """
