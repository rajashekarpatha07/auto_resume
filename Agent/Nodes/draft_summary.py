from dotenv import load_dotenv
from Agent.prompts.resume import build_summary_prompt
from Agent.schemas.resume import GraphState, SummarySchema
from Agent.tools.knowledge import read_knowledge_json
from Agent.llm.local_llm import llm
from Agent.utils.retry import invoke_with_retry

load_dotenv()

SUMMARY_FILE = "summery.json"

summary_llm = llm.with_structured_output(SummarySchema)


def draft_summary_node(state: GraphState) -> dict:
    summary_info = read_knowledge_json.invoke({"filename": SUMMARY_FILE})
    prompt = build_summary_prompt(
        jd_json=state["jd_json"],
        summary_info=summary_info,
        previous_draft=state.get("summary_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: SummarySchema = invoke_with_retry(summary_llm, prompt)

    return {
        "summary_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "summary",
    }
