from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from Agent.prompts.resume import build_parse_jd_prompt
from Agent.schemas.resume import GraphState, SkillsSchema
from Agent.tools.knowledge import read_knowledge_json

load_dotenv()

llm = ChatOllama(model="qwen3:4b", temperature=0.2)

skills_llm = llm.with_structured_output(SkillsSchema)

SKILLS_FILE = "skills.json"


def draft_skills_node(state: GraphState) -> dict:
    skills_info = read_knowledge_json.invoke({"filename": SKILLS_FILE})

    feedback_block = ""
    if state.get("review_feedback"):
        feedback_block = f"""
        The reviewer rejected the previous draft. Revise it using this feedback:
        Previous draft: {state.get("skills_draft")}
        Feedback: {state["review_feedback"]}
        """

    prompt = f"""
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
    {state["jd_json"]}

    Candidate skills data (JSON):
    {skills_info}
    {feedback_block}
    """
    draft: SkillsSchema = skills_llm.invoke(prompt)
    return {
        "skills_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "skills",
    }
