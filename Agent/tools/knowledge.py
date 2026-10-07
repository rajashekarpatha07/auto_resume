import json
from pathlib import Path

from langchain_core.tools import tool

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


@tool
def read_knowledge_json(filename: str) -> str:
    """Read a JSON file from the Agent knowledge folder by filename."""
    candidate = (KNOWLEDGE_DIR / filename).resolve()
    if candidate.parent != KNOWLEDGE_DIR.resolve() or candidate.suffix.lower() != ".json":
        raise ValueError("filename must name a JSON file in the knowledge folder")
    if not candidate.is_file():
        raise FileNotFoundError(f"Knowledge JSON file not found: {filename}")

    with candidate.open(encoding="utf-8") as knowledge_file:
        return json.dumps(json.load(knowledge_file), ensure_ascii=False, indent=2)
