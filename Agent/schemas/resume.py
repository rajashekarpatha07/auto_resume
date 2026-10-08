from typing import List, NotRequired, Optional, Literal

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

SKILLS_FILE = "skills.json"  # change if your file is named differently


class SkillCategory(BaseModel):
    category: str = Field(
        description="Short category label, e.g. 'Languages', 'Backend & APIs'"
    )
    skills: List[str] = Field(
        description="Skills in this category, most JD-relevant first"
    )


class SkillsSchema(BaseModel):
    categories: List[SkillCategory] = Field(
        description="3 to 5 skill categories, ordered by relevance to the job description"
    )


class JobDescriptionSchema(BaseModel):
    job_title: str = Field(description="The official title of the job position")
    company_name: Optional[str] = Field(
        None, description="Name of the company hiring, if available"
    )
    location: Optional[str] = Field(None, description="Job location or remote status")
    required_skills: List[str] = Field(
        description="List of mandatory technical and soft skills"
    )
    experience_years: Optional[str] = Field(
        None, description="Minimum years of experience required"
    )
    key_responsibilities: List[str] = Field(
        description="List of primary duties and responsibilities"
    )
    salary_range: Optional[str] = Field(
        None, description="Compensation or salary range if mentioned"
    )


class SummarySchema(BaseModel):
    summary: str = Field(
        description="Professional summary of 4 to 5 sentences (about 60-90 words), "
        "tailored to the job description"
    )


class ResumeHeaderSchema(BaseModel):
    full_name: str = Field(
        description="Candidate's full name exactly as in personal info"
    )
    headline: str = Field(
        description="One-line professional headline tailored to the JD job title, "
        "supported by the candidate's real background"
    )
    contact_items: List[str] = Field(
        description="Contact details (email, phone, location, LinkedIn, GitHub, "
        "portfolio) copied from personal info; only include what exists"
    )


class ProjectItem(BaseModel):
    name: str = Field(
        description="Project name, copied exactly as in the candidate data"
    )
    tech_stack: List[str] = Field(
        description="Technologies used, only those listed for this project in the candidate data"
    )
    bullets: List[str] = Field(
        description="2 to 3 concise bullets describing what was built and the outcome"
    )
    link: Optional[str] = Field(
        None, description="GitHub/demo URL, only if present in the candidate data"
    )


class ProjectsSchema(BaseModel):
    projects: List[ProjectItem] = Field(
        description="The 2 to 4 projects most relevant to the job, most relevant first"
    )


EDUCATION_FILE = "education.json"


class EducationItem(BaseModel):
    institution: str = Field(
        description="School/college/university name, copied exactly from the data"
    )
    degree: str = Field(
        description="Degree or qualification, e.g. 'B.Tech in Computer Science', copied exactly"
    )
    duration: Optional[str] = Field(
        None, description="Start-end years, only if present in the data"
    )
    grade: Optional[str] = Field(
        None, description="CGPA/percentage, only if present in the data"
    )
    location: Optional[str] = Field(
        None, description="City/state, only if present in the data"
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="0 to 2 short items (relevant coursework, honors), only if present in the data",
    )


class EducationSchema(BaseModel):
    education: List[EducationItem] = Field(
        description="Education entries, most recent first"
    )
    extracurriculars: List[str] = Field(
        default_factory=list,
        description=(
            "0 to 3 extracurricular activities (clubs, hackathons, volunteering, "
            "leadership roles), only if present in the data AND useful for the target job"
        ),
    )


class SkillAddition(BaseModel):
    skill: str = Field(description="Skill name, exactly as in the candidate data")
    category: str = Field(
        description="Existing category from the skills draft where it fits best"
    )


class OptimizationSchema(BaseModel):
    section_order: List[Literal["summary", "skills", "projects", "education"]] = Field(
        description="Order of the sections after the header, best for this job first. Include all four."
    )
    skills_to_add: List[SkillAddition] = Field(
        default_factory=list,
        description="JD-relevant skills missing from the resume but present in the candidate data",
    )
    gaps: List[str] = Field(
        default_factory=list,
        description="JD requirements with NO evidence in the candidate data (report only)",
    )
    notes: str = Field(
        "", description="One or two sentences explaining the ordering choice"
    )
    covered_keywords: List[str] = Field(default_factory=list)  # filled in Python
    missing_keywords: List[str] = Field(default_factory=list)  # filled in Python


class GraphState(TypedDict):
    jd_text: str
    jd_json: Optional[dict]
    knowledge_file: NotRequired[str]
    current_section: NotRequired[str]
    approved_sections: NotRequired[List[str]]
    header_draft: NotRequired[dict]
    summary_draft: NotRequired[dict]
    review_feedback: NotRequired[str]
    docx_path: NotRequired[str]
    skills_draft: NotRequired[dict]
    projects_draft: NotRequired[dict]
    education_draft: NotRequired[dict]
    optimization_draft: NotRequired[dict]


SECTION_SCHEMAS = {
    "header": ResumeHeaderSchema,
    "summary": SummarySchema,
    "projects": ProjectsSchema,
    "education": EducationSchema,
}
