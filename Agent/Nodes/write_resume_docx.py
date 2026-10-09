from pathlib import Path
import re
from Agent.schemas.resume import (
    EducationSchema,
    GraphState,
    ProjectsSchema,
    ResumeHeaderSchema,
    SkillsSchema,
    SummarySchema,
)
from Agent.tools.docx_builder import build_resume_docx

OUTPUT_DIR = Path("output")
DEFAULT_SECTION_ORDER = ["summary", "skills", "projects", "education"]


# ──────────────── Markdown preview (kept for quick inspection) ────────────────


def _resume_to_markdown(header, summary, skills, projects, education, section_order):
    parts = [
        f"# {header.full_name}\n\n"
        f"**{header.headline}**\n\n"
        f"{' | '.join(header.contact_items)}\n",
    ]

    section_md = {
        "summary": f"## Summary\n\n{summary.summary}\n",
        "skills": "## Skills\n\n"
        + "\n".join(
            f"- **{c.category}:** {', '.join(c.skills)}" for c in skills.categories
        )
        + "\n",
        "projects": "## Projects\n\n"
        + "\n\n".join(_project_md(p) for p in projects.projects)
        + "\n",
        "education": "## Education\n\n" + _education_md(education) + "\n",
    }

    for name in section_order:
        if name in section_md:
            parts.append(section_md[name])

    return "\n".join(parts)


def _project_md(p):
    title = f"### {p.name}"
    if p.link:
        title += f" | {p.link}"
    bullets = "\n".join(f"- {b}" for b in p.bullets)
    return f"{title}\n\n*{', '.join(p.tech_stack)}*\n\n{bullets}"


def _education_md(education):
    blocks = []
    for e in education.education:
        meta = " | ".join(x for x in [e.duration, e.grade, e.location] if x)
        block = f"### {e.institution}\n\n**{e.degree}**"
        if meta:
            block += f"\n\n{meta}"
        if e.highlights:
            block += "\n\n" + "\n".join(f"- {h}" for h in e.highlights)
        blocks.append(block)

    md = "\n\n".join(blocks)
    if education.extracurriculars:
        lines = "\n".join(f"- {a}" for a in education.extracurriculars)
        md += f"\n\n**Extracurricular Activities**\n\n{lines}"
    return md


# ──────────────── Node ────────────────


def write_resume_docx_node(state: GraphState) -> dict:
    approved = state.get("approved_sections", [])
    required = {"header", "summary", "skills", "projects", "education", "optimization"}
    if not required <= set(approved):
        raise ValueError(f"Sections not fully approved yet: {approved}")

    header = ResumeHeaderSchema(**state["header_draft"])
    summary = SummarySchema(**state["summary_draft"])
    skills = SkillsSchema(**state["skills_draft"])
    projects = ProjectsSchema(**state["projects_draft"])
    education = EducationSchema(**state["education_draft"])

    # Use section order from the optimization node if available
    section_order = DEFAULT_SECTION_ORDER
    if opt := state.get("optimization_draft"):
        section_order = opt.get("section_order", DEFAULT_SECTION_ORDER)

    jd_data = state.get("jd_json", {})
    company_name = jd_data.get("company_name") or "UnknownCompany"
    job_title = jd_data.get("job_title") or "Role"

    safe_company = re.sub(r"[^\w\-]", "_", company_name).strip("_")
    safe_title = re.sub(r"[^\w\-]", "_", job_title).strip("_")

    file_name = f"{safe_company}_{safe_title}_Resume"

    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = (OUTPUT_DIR / f"{file_name}_Resume").resolve()
    docx_path = (OUTPUT_DIR / f"{file_name}_Resume").resolve()

    # Markdown preview
    md_path.write_text(
        _resume_to_markdown(
            header, summary, skills, projects, education, section_order
        ),
        encoding="utf-8",
    )

    # Professional DOCX
    build_resume_docx(
        doc_path=docx_path,
        header=header,
        summary=summary,
        skills=skills,
        projects=projects,
        education=education,
        section_order=section_order,
    )

    return {"docx_path": str(docx_path)}
