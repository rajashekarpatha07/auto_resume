from Agent.schemas.resume import GraphState, ProjectsSchema
from Agent.tools.knowledge import read_knowledge_json
from Agent.llm.local_llm import llm

PROJECTS_FILE = "projects.json"

projects_llm = llm.with_structured_output(ProjectsSchema)

def draft_projects_node(state: GraphState) -> dict:
    projects_info = read_knowledge_json.invoke({"filename": PROJECTS_FILE})

    feedback_block = ""
    if state.get("review_feedback"):
        feedback_block = f"""
        The reviewer rejected the previous draft. Revise it using this feedback:
        Previous draft: {state.get("projects_draft")}
        Feedback: {state["review_feedback"]}
        """

    prompt = f"""
    You are an expert resume writer. Build the PROJECTS section of a resume,
    tailored to the target job.

    Strict rules (accuracy matters more than impressiveness):
    - Select only the 2 to 4 projects from the candidate data that best match
      the job. Copy project names exactly. Never invent a project.
    - Use ONLY facts stated in the candidate data. Do NOT invent or estimate
      metrics, percentages, user counts, performance gains, or team sizes.
      If the data has no numbers, write no numbers.
    - tech_stack must only contain technologies listed for that project.
      Do not add a technology just because the job asks for it.
    - Each project gets 2 to 3 bullets. Start each with a strong action verb
      (Built, Designed, Implemented), keep each under about 25 words.
    - Reword for relevance to the job (emphasize matching keywords), but never
      upgrade the scope of the work (e.g. "contributed to" must not become "led").
    - Include a link only if one is present in the data.

    Target job (structured):
    {state["jd_json"]}

    Candidate projects data (JSON):
    {projects_info}

    {feedback_block}
    """

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