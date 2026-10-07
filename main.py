from langgraph.types import Command

from Agent.graph.resume_graph import graph


MOCK_JD = """
Backend Developer Intern
TechNova Systems, Hyderabad, India (Hybrid)

About the role:
We are looking for a Backend Developer Intern to help design, build and maintain
scalable backend services and APIs. You will work closely with frontend and
engineering teams to develop reliable backend systems and real-time features.

Responsibilities:
- Build and maintain REST APIs using TypeScript and Node.js
- Develop backend services using Express.js or similar frameworks
- Design and optimize MongoDB schemas, queries, and indexes
- Use Redis for caching, session management, and performance optimization
- Implement real-time features using WebSockets and Socket.io
- Write clean, maintainable, and well-tested backend code
- Debug issues, improve API performance, and monitor backend services
- Collaborate with frontend developers and other engineers to deliver features

Requirements:
- Currently pursuing a degree in Computer Science, Software Engineering, or a related field
- Strong understanding of JavaScript and TypeScript
- Familiarity with Node.js and Express.js
- Basic experience with MongoDB and database design
- Understanding of Redis and caching concepts
- Familiarity with WebSockets or Socket.io
- Understanding of REST APIs, HTTP, and authentication concepts
- Familiarity with Git and GitHub
- Good problem-solving and communication skills

Nice to have:
- Experience building and deploying backend projects
- Familiarity with Docker and Linux
- Understanding of JWT authentication
- Basic knowledge of system design and scalable backend architecture
- Experience with message queues such as BullMQ or Kafka
- Familiarity with AWS or other cloud platforms

Compensation: INR 20,000-35,000 per month
"""


def run_demo() -> None:
    config = {"configurable": {"thread_id": "test-run-3"}}
    result = graph.invoke({"jd_text": MOCK_JD}, config)

    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(f"\n--- {payload['section'].upper()} DRAFT ---")
        print(payload["draft"])

        choice = input("\n[a]pprove / [r]evise: ").strip().lower()
        if choice == "a":
            resume = {"action": "approve"}
        else:
            resume = {"action": "revise", "feedback": input("Feedback: ")}

        result = graph.invoke(Command(resume=resume), config)

    print("\nDone. DOCX saved at:", result["docx_path"])


if __name__ == "__main__":
    run_demo()
