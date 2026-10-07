from typing import List, NotRequired, Optional

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


SECTION_SCHEMAS = {"header": ResumeHeaderSchema, "summary": SummarySchema}
