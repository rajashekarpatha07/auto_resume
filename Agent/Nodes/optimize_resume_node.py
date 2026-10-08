from Agent.llm.local_llm import llm
from Agent.schemas.resume import OptimizationSchema, GraphState
from Agent.tools.knowledge import read_knowledge_json



SUMMARY_FILE="summery.json"
SKILLS_FILE="skills.json"
PROJECTS_FILE="projects.json"
EDUCATION_FILE="education.json"



optimizer_llm = llm.with_structured_output(OptimizationSchema)

def _keyword_coverage(jd_json: dict, state: GraphState) -> tuple[list, list]:
    resume_text = " ".join(
        str(state.get(k, "")) for k in
        ("header_draft", "summary_draft", "skills_draft", "projects_draft", "education_draft")
    ).lower()
    keywords = jd_json.get("required_skills", [])
    covered = [k for k in keywords if k.lower() in resume_text]
    missing = [k for k in keywords if k.lower() not in resume_text]
    return covered, missing

def optimize_resume_node(state: GraphState) -> dict:
    covered, missing = _keyword_coverage(state["jd_json"], state)

    knowledge = {
        f: read_knowledge_json.invoke({"filename": f})
        for f in (SUMMARY_FILE, SKILLS_FILE, PROJECTS_FILE, EDUCATION_FILE)
    }

    feedback_block = ""
    if state.get("review_feedback"):
        feedback_block = f"""
        The reviewer rejected the previous result. Revise it using this feedback:
        Previous result: {state.get("optimization_draft")}
        Feedback: {state["review_feedback"]}
        """

    prompt = f"""
    You are an expert resume strategist doing a final pass on a resume.

    Target job (structured):
    {state["jd_json"]}

    Current resume sections (already approved by the candidate):
    Summary: {state["summary_draft"]}
    Skills: {state["skills_draft"]}
    Projects: {state["projects_draft"]}
    Education: {state["education_draft"]}

    JD keywords NOT yet visible in the resume: {missing}

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

    draft: OptimizationSchema = optimizer_llm.invoke(prompt)

    # Grounding check: every added skill must exist somewhere in the candidate data
    source = str(knowledge).lower()
    draft.skills_to_add = [
        s for s in draft.skills_to_add
        if (s.skill.lower() in source) or print(f"DROPPED ungrounded skill: {s.skill}")
    ]

    draft.covered_keywords = covered
    draft.missing_keywords = missing

    return {
        "optimization_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "optimization",
    }