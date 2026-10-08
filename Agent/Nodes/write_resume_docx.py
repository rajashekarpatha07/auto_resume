import asyncio
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

from Agent.schemas.resume import (
    GraphState,
    ResumeHeaderSchema,
    SummarySchema,
    SkillsSchema,
    ProjectsSchema,
)

OUTPUT_DIR = Path("output")

DOCX_MCP_CONFIG = {
    "docx": {
        "command": "uvx",
        "args": ["--with", "mcp<2", "docx-mcp-server"],
        "transport": "stdio",
    }
}


async def _write_docx_via_mcp(md_path: Path, docx_path: Path) -> None:
    client = MultiServerMCPClient(DOCX_MCP_CONFIG)
    tools = await client.get_tools()
    tool = next(
        (
            candidate
            for candidate in tools
            if "docx" in f"{candidate.name} {candidate.description}".lower()
            and any(
                word in f"{candidate.name} {candidate.description}".lower()
                for word in ("markdown", "convert", "create")
            )
        ),
        None,
    )
    if tool is None:
        raise RuntimeError("The DOCX MCP server has no Markdown-to-DOCX tool")

    markdown = md_path.read_text(encoding="utf-8")
    arguments = {}
    for name in tool.args:
        key = name.lower()
        if any(word in key for word in ("output", "destination")):
            arguments[name] = str(docx_path)
        elif any(word in key for word in ("markdown", "content", "text")):
            arguments[name] = markdown
        elif any(word in key for word in ("input", "source", "file", "path")):
            arguments[name] = str(md_path)

    await tool.ainvoke(arguments)


def _resume_to_markdown(
    header: ResumeHeaderSchema,
    summary: SummarySchema,
    skills: SkillsSchema,
    projects: ProjectsSchema,
) -> str:
    skill_lines = "\n".join(
        f"- **{c.category}:** {', '.join(c.skills)}" for c in skills.categories
    )

    project_blocks = []
    for p in projects.projects:
        title = f"### {p.name}"
        if p.link:
            title += f" | {p.link}"
        bullets = "\n".join(f"- {b}" for b in p.bullets)
        project_blocks.append(f"{title}\n\n*{', '.join(p.tech_stack)}*\n\n{bullets}")

    return (
        f"# {header.full_name}\n\n"
        f"**{header.headline}**\n\n"
        f"{' | '.join(header.contact_items)}\n\n"
        f"## Summary\n\n{summary.summary}\n\n"
        f"## Skills\n\n{skill_lines}\n\n"
        f"## Projects\n\n" + "\n\n".join(project_blocks) + "\n"
    )


def write_resume_docx_node(state: GraphState) -> dict:
    approved = state.get("approved_sections", [])
    if not {"header", "summary", "skills", "projects"} <= set(approved):
        raise ValueError(f"Sections not fully approved yet: {approved}")

    header = ResumeHeaderSchema(**state["header_draft"])
    summary = SummarySchema(**state["summary_draft"])
    skills = SkillsSchema(**state["skills_draft"])
    projects = ProjectsSchema(**state["projects_draft"])

    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = (OUTPUT_DIR / "resume.md").resolve()
    docx_path = (OUTPUT_DIR / "resume.docx").resolve()

    md_path.write_text(
        _resume_to_markdown(header, summary, skills, projects), encoding="utf-8"
    )
    docx_path.unlink(missing_ok=True)

    asyncio.run(_write_docx_via_mcp(md_path, docx_path))
    return {"docx_path": str(docx_path)}
