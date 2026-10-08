from Agent.llm.local_llm import llm
from Agent.tools.knowledge import read_knowledge_json
from Agent.schemas.resume import EducationSchema, GraphState

EDUCATION_FILE = "education.json"
education_llm = llm.with_structured_output(EducationSchema)


def draft_education_node(state: GraphState) -> dict:
    education_info = read_knowledge_json.invoke({"filename": EDUCATION_FILE})

    feedback_block = ""
    if state.get("review_feedback"):
        feedback_block = f"""
        The reviewer rejected the previous draft. Revise it using this feedback:
        Previous draft: {state.get("education_draft")}
        Feedback: {state["review_feedback"]}
        """

    prompt = f"""
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
    {state["jd_json"]}

    Candidate education data (JSON):
    {education_info}

    {feedback_block}
    """

    draft: EducationSchema = education_llm.invoke(prompt)

    # Cheap grounding check: flag institutions that don't appear in the source
    for a in draft.extracurriculars:
        if a.lower() not in str(education_info).lower():
            print(
                f"WARNING: extracurricular '{a}' not found verbatim in {EDUCATION_FILE}, check it carefully"
            )

    return {
        "education_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "education",
    }
