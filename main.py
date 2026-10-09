import json

from langgraph.types import Command

from Agent.graph.resume_graph import graph

MOCK_JD = """
Job Description:
what is CRED?

CRED is an exclusive community for India's most trustworthy and creditworthy individuals, where members are rewarded for good financial behavior. CRED was born out of a need to bring back the focus on a long-lost virtue of -‘trust’- the idea being to create a community centered around it. a community that constantly strives to become more virtuous in this regard, till it finally scales that behavior to create a utopia where being trustworthy is the norm, not the exception. Building a community like this requires a community of its own - one that's special in its own way, working towards making this vision come true.

here's a thought experiment: what do you get when you put a group of incredibly passionate and driven people and hand them the complete freedom to chase their goals in a completely uninhibited manner? Answer: you get something close to what we have at CRED. CRED just has it better.

here's what's in store for you at CRED once you join as a backend engineering intern - in 2026, that means building with AI as a core part of how you work, not as an afterthought.
what you will do:

    you will be working on solving real problems with sustainable guidance from experienced mentors.
    design, build, test, and ship features and services, applying an AI-native engineering workflow by default: using coding agents and LLM tooling - while owning the judgment on what ships.
    write code that's correct under edge cases, not just code that "looks right" to an autocomplete - apply real software engineering fundamentals (testing, system design basics, data structures, APIs) as the backbone under any AI-assisted workflow.
    own the outcomes of the areas you're responsible for, end to end - including their reliability once they're live

you should apply If you have:

    proficiency in at least one programming language (java, python, golang, java script etc.)
    clear fundamentals in computer programming and problem solving - you understand the concepts, not just the syntax
    comfort leveraging AI tools - Copilot, Cursor, Claude Code, ChatGPT, or similar; in your day-to-day work
    the judgment to know when to trust AI-generated output and when to slow down and verify it yourself - you can explain why code works, not just that it compiled
    curiosity to learn, adapt, and constantly improve both yourself and your work
    ability to navigate ambiguity and thrive in evolving environments
    zeal for building products with empathy for customers
    prior internship experience is a plus - it can help you sail through faster at CRED, but it isn't mandatory

how is life at CRED?

working at CRED would instantly make you realize one thing: you are working with the best talent around you. not just in the role you occupy, but everywhere you go. talk to someone around you; most likely you will be talking to a singer, standup comic, artist, writer, an athlete, maybe a magician. at CRED people always have talent up their sleeves. with the right company, even conversations can be rejuvenating. at CRED, we guarantee a good company.

hard truths: pushing oneself comes with the role and we realise pushing oneself is hard work. which is why CRED is in the continuous process of building an environment that helps the team rejuvenate oneself: included but not limited to a stacked, in-house pantry, with lunch and dinner provided for all the team members, paid sick leaves and comprehensive health insurance.

to make things smoother and to make sure you spend time and energy only on the most important things, CRED strives to make every process transparent: there are no work timings because we do not believe in archaic methods of calculating productivity, your work should speak for you. there are no job designations because you will be expected to hold down roles that cannot be described in one word.

there are many more such eccentricities that make CRED what it is but that’s for one to discover. if you feel at home reading this, get in touch.
eligibility criteria

2027 passout
"""


def _format_draft(section: str, draft: dict) -> str:
    """Pretty-print a draft for human review."""
    lines = [f"\n{'='*60}", f"  {section.upper()} DRAFT", f"{'='*60}"]

    if section == "header":
        lines.append(f"  Name:     {draft.get('full_name', '')}")
        lines.append(f"  Headline: {draft.get('headline', '')}")
        for item in draft.get("contact_items", []):
            lines.append(f"  • {item}")

    elif section == "summary":
        lines.append(f"\n  {draft.get('summary', '')}")

    elif section == "skills":
        for cat in draft.get("categories", []):
            skills = ", ".join(cat.get("skills", []))
            lines.append(f"  {cat.get('category', '')}: {skills}")

    elif section == "projects":
        for p in draft.get("projects", []):
            lines.append(
                f"\n  ► {p.get('name', '')}  [{', '.join(p.get('tech_stack', []))}]"
            )
            for b in p.get("bullets", []):
                lines.append(f"    • {b}")
            if p.get("link"):
                lines.append(f"    🔗 {p['link']}")

    elif section == "education":
        for e in draft.get("education", []):
            meta = " | ".join(
                x for x in [e.get("duration"), e.get("grade"), e.get("location")] if x
            )
            lines.append(f"\n  ► {e.get('institution', '')}")
            lines.append(f"    {e.get('degree', '')}" + (f"  ({meta})" if meta else ""))
            for h in e.get("highlights", []):
                lines.append(f"    • {h}")
        for a in draft.get("extracurriculars", []):
            lines.append(f"    ○ {a}")

    elif section == "optimization":
        lines.append(f"  Section order: {' → '.join(draft.get('section_order', []))}")
        if draft.get("skills_to_add"):
            lines.append("  Skills to add:")
            for s in draft["skills_to_add"]:
                lines.append(f"    + {s.get('skill', '')} → [{s.get('category', '')}]")
        if draft.get("gaps"):
            lines.append("  Gaps (JD requirements with no evidence):")
            for g in draft["gaps"]:
                lines.append(f"    ✗ {g}")
        covered = draft.get("covered_keywords", [])
        missing = draft.get("missing_keywords", [])
        if covered or missing:
            lines.append(
                f"  Keyword coverage: {len(covered)}/{len(covered)+len(missing)}"
            )
        if draft.get("notes"):
            lines.append(f"  Notes: {draft['notes']}")

    else:
        lines.append(json.dumps(draft, indent=2))

    lines.append(f"{'='*60}")
    return "\n".join(lines)


def run_demo() -> None:
    config = {"configurable": {"thread_id": "test-run-3"}}
    result = graph.invoke({"jd_text": MOCK_JD}, config)

    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        section = payload["section"]
        draft = payload["draft"]

        print(_format_draft(section, draft))

        choice = input("\n[a]pprove / [r]evise: ").strip().lower()
        if choice == "a":
            resume = {"action": "approve"}
        else:
            resume = {"action": "revise", "feedback": input("Feedback: ")}

        result = graph.invoke(Command(resume=resume), config)

    print(f"\n✓ Done. DOCX saved at: {result['docx_path']}")


if __name__ == "__main__":
    run_demo()
