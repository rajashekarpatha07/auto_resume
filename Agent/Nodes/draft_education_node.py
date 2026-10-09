from Agent.prompts.resume import build_education_prompt
from Agent.schemas.resume import EducationSchema, GraphState
from Agent.tools.knowledge import read_knowledge_json
from Agent.llm.local_llm import llm
from Agent.utils.retry import invoke_with_retry

EDUCATION_FILE = "education.json"
education_llm = llm.with_structured_output(EducationSchema)


def draft_education_node(state: GraphState) -> dict:
    education_info = read_knowledge_json.invoke({"filename": EDUCATION_FILE})
    prompt = build_education_prompt(
        jd_json=state["jd_json"],
        education_info=education_info,
        previous_draft=state.get("education_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: EducationSchema = invoke_with_retry(education_llm, prompt)

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
