from typing import Literal

from langgraph.types import Command, interrupt

from Agent.schemas.resume import (
    GraphState,
    SECTION_SCHEMAS,
    ResumeHeaderSchema,
    SummarySchema,
    SkillsSchema,
    ProjectsSchema,
)

SECTION_SCHEMAS = {
    "header": ResumeHeaderSchema,
    "summary": SummarySchema,
    "skills": SkillsSchema,
    "projects": ProjectsSchema,
}

DRAFT_NODE = {
    "header": "draft_header",
    "summary": "draft_summary",
    "skills": "draft_skills",
    "projects": "draft_projects",
}

NEXT_AFTER_APPROVAL = {
    "header": "draft_summary",
    "summary": "draft_skills",
    "skills": "draft_projects",  
    "projects": "write_resume_docx",  
}


def human_review_node(
    state: GraphState,
) -> Command[
    Literal["draft_header", "draft_summary", "draft_skills", "draft_projects", "write_resume_docx", ]]:
    section = state["current_section"]
    draft_key = f"{section}_draft"

    decision = interrupt(
        {
            "section": section,
            "draft": state[draft_key],
            "expected_response": {
                "approve": {"action": "approve"},
                "edit": {"action": "edit", "content": "<full dict for this section>"},
                "revise": {"action": "revise", "feedback": "<what to change>"},
            },
        }
    )

    action = decision.get("action")
    approved = state.get("approved_sections", [])

    if action in ("approve", "edit"):
        update = {"approved_sections": approved + [section], "review_feedback": ""}
        if action == "edit":
            update[draft_key] = SECTION_SCHEMAS[section](
                **decision["content"]
            ).model_dump()
        return Command(goto=NEXT_AFTER_APPROVAL[section], update=update)

    return Command(
        goto=DRAFT_NODE[section],
        update={
            "review_feedback": decision.get("feedback", "Please improve the draft.")
        },
    )
