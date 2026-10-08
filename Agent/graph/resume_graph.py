from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from Agent.Nodes.draft_header import draft_header_node
from Agent.Nodes.draft_summary import draft_summary_node
from Agent.Nodes.human_review import human_review_node
from Agent.Nodes.parse_jd import parse_jd_node
from Agent.Nodes.write_resume_docx import write_resume_docx_node
from Agent.Nodes.draft_skills_node import draft_skills_node
from Agent.Nodes.draft_projects_node import draft_projects_node
from Agent.schemas.resume import GraphState


def build_resume_graph():
    builder = StateGraph(GraphState)
    builder.add_node("parse_jd", parse_jd_node)
    builder.add_node("draft_header", draft_header_node)
    builder.add_node("draft_summary", draft_summary_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("write_resume_docx", write_resume_docx_node)
    builder.add_node("draft_projects", draft_projects_node)
    builder.add_node("draft_skills", draft_skills_node)

    builder.add_edge(START, "parse_jd")
    builder.add_edge("parse_jd", "draft_header")
    builder.add_edge("draft_header", "human_review")
    builder.add_edge("draft_summary", "human_review")
    builder.add_edge("draft_skills", "human_review")
    builder.add_edge("draft_projects", "human_review")
    
    builder.add_edge("write_resume_docx", END)

    return builder.compile(checkpointer=MemorySaver())


graph = build_resume_graph()
