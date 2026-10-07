from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from Agent.prompts.resume import build_header_prompt
from Agent.schemas.resume import GraphState, ResumeHeaderSchema
from Agent.tools.knowledge import read_knowledge_json

load_dotenv()

PERSONAL_INFO_FILE = "Personal_info.json"

llm = ChatOllama(model="qwen3:4b", temperature=0.2)
header_llm = llm.with_structured_output(ResumeHeaderSchema)


def draft_header_node(state: GraphState) -> dict:
    personal_info = read_knowledge_json.invoke({"filename": PERSONAL_INFO_FILE})
    prompt = build_header_prompt(
        jd_json=state["jd_json"],
        personal_info=personal_info,
        previous_draft=state.get("header_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: ResumeHeaderSchema = header_llm.invoke(prompt)

    return {
        "header_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "header",
    }
