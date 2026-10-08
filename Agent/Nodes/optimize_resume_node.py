from Agent.llm.local_llm import llm
from Agent.prompts.resume import build_optimization_prompt
from Agent.schemas.resume import OptimizationSchema, GraphState
from Agent.tools.knowledge import read_knowledge_json


SUMMARY_FILE = "summery.json"
SKILLS_FILE = "skills.json"
PROJECTS_FILE = "projects.json"
EDUCATION_FILE = "education.json"


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

    prompt = build_optimization_prompt(
        jd_json=state["jd_json"],
        summary_draft=state["summary_draft"],
        skills_draft=state["skills_draft"],
        projects_draft=state["projects_draft"],
        education_draft=state["education_draft"],
        missing_keywords=missing,
        knowledge=knowledge,
        previous_draft=state.get("optimization_draft"),
        review_feedback=state.get("review_feedback"),
    )

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