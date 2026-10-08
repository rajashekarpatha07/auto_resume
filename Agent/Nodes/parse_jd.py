from dotenv import load_dotenv
from Agent.llm.local_llm import llm
from Agent.prompts.resume import build_parse_jd_prompt
from Agent.schemas.resume import GraphState, JobDescriptionSchema
from Agent.tools.knowledge import read_knowledge_json

load_dotenv()

structured_llm = llm.with_structured_output(JobDescriptionSchema)


def parse_jd_node(state: GraphState) -> GraphState:
    knowledge_json = None
    if knowledge_file := state.get("knowledge_file"):
        knowledge_json = read_knowledge_json.invoke({"filename": knowledge_file})

    prompt = build_parse_jd_prompt(state["jd_text"], knowledge_json)
    parsed_jd: JobDescriptionSchema = structured_llm.invoke(prompt)
    print(parsed_jd)

    return {"jd_json": parsed_jd.model_dump()}
