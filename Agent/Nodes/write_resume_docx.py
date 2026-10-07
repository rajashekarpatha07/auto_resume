import asyncio
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from Agent.schemas.resume import (
    GraphState,
    ResumeHeaderSchema,
    SummarySchema,
    SkillsSchema,
)

OUTPUT_DIR = Path("output")

DOCX_MCP_CONFIG = {
    "docx": {
        "command": "uvx",
        "args": ["--with", "mcp<2", "docx-mcp-server"],
        "transport": "stdio",
    }
}


def _resume_to_markdown(
    header: ResumeHeaderSchema, summary: SummarySchema, skills: SkillsSchema
) -> str:
    skill_lines = "\n".join(
        f"- **{c.category}:** {', '.join(c.skills)}" for c in skills.categories
    )
    return (
        f"# {header.full_name}\n\n"
        f"**{header.headline}**\n\n"
        f"{' | '.join(header.contact_items)}\n\n"
        f"## Summary\n\n"
        f"{summary.summary}\n\n"
        f"## Skills\n\n"
        f"{skill_lines}\n"
    )


async def _write_docx_via_mcp(md_path: Path, docx_path: Path) -> None:
    client = MultiServerMCPClient(DOCX_MCP_CONFIG)
    async with client.session("docx") as session:
        tools = {t.name: t for t in await load_mcp_tools(session)}
        await tools["create_from_markdown"].ainvoke(
            {"path": str(docx_path), "md_path": str(md_path)}
        )
        await tools["save_document"].ainvoke({})


def write_resume_docx_node(state: GraphState) -> dict:
    approved = state.get("approved_sections", [])
    if not {"header", "summary", "skills"} <= set(approved):
        raise ValueError(f"Sections not fully approved yet: {approved}")

    header = ResumeHeaderSchema(**state["header_draft"])
    summary = SummarySchema(**state["summary_draft"])
    skills = SkillsSchema(**state["skills_draft"])

    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = (OUTPUT_DIR / "resume.md").resolve()
    docx_path = (OUTPUT_DIR / "resume.docx").resolve()
    md_path.write_text(_resume_to_markdown(header, summary, skills), encoding="utf-8")
    docx_path.unlink(missing_ok=True)

    asyncio.run(_write_docx_via_mcp(md_path, docx_path))
    return {"docx_path": str(docx_path)}
