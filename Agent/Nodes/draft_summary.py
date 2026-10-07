from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from Agent.prompts.resume import build_summary_prompt
from Agent.schemas.resume import GraphState, SummarySchema
from Agent.tools.knowledge import read_knowledge_json

load_dotenv()

SUMMARY_FILE = "summery.json"

llm = ChatOllama(model="qwen3:4b", temperature=0.2)
summary_llm = llm.with_structured_output(SummarySchema)


def draft_summary_node(state: GraphState) -> dict:
    summary_info = read_knowledge_json.invoke({"filename": SUMMARY_FILE})
    prompt = build_summary_prompt(
        jd_json=state["jd_json"],
        summary_info=summary_info,
        previous_draft=state.get("summary_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: SummarySchema = summary_llm.invoke(prompt)

    return {
        "summary_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "summary",
    }
