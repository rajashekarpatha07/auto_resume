from Agent.prompts.resume import build_projects_prompt
from Agent.schemas.resume import GraphState, ProjectsSchema
from Agent.tools.knowledge import read_knowledge_json
from Agent.llm.local_llm import llm

PROJECTS_FILE = "projects.json"

projects_llm = llm.with_structured_output(ProjectsSchema)


def draft_projects_node(state: GraphState) -> dict:
    projects_info = read_knowledge_json.invoke({"filename": PROJECTS_FILE})
    prompt = build_projects_prompt(
        jd_json=state["jd_json"],
        projects_info=projects_info,
        previous_draft=state.get("projects_draft"),
        review_feedback=state.get("review_feedback"),
    )
    draft: ProjectsSchema = projects_llm.invoke(prompt)

    # Cheap grounding check: flag project names that don't appear in the source
    for p in draft.projects:
        if p.name.lower() not in str(projects_info).lower():
            print(f"WARNING: project '{p.name}' not found in {PROJECTS_FILE}, check it carefully")

    return {
        "projects_draft": draft.model_dump(),
        "review_feedback": "",
        "current_section": "projects",
    }