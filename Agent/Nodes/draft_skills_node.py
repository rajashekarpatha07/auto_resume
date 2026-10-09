from dotenv import load_dotenv
from Agent.prompts.resume import build_skills_prompt
from Agent.schemas.resume import GraphState, SkillsSchema
from Agent.tools.knowledge import read_knowledge_json
from Agent.llm.local_llm import llm
from Agent.utils.retry import invoke_with_retry

load_dotenv()

skills_llm = llm.with_structured_output(SkillsSchema)

SKILLS_FILE = "skills.json"


def draft_skills_node(state: GraphState) -> dict:
    skills_info = read_knowledge_json.invoke({"filename": SKILLS_FILE})
    prompt = build_skills_prompt(
        jd_json=state["jd_json"],
        skills_info=skills_info,
        previous_draft=state.get("skills_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: SkillsSchema = invoke_with_retry(skills_llm, prompt)
    return {
        "skills_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "skills",
    }
