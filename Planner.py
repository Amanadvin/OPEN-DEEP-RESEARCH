# planner.py
from openai import OpenAI

client = OpenAI(
    base_url="http://10.205.85.250:1234",
    api_key="lm-studio",
    timeout=180
)
def planner_agent(topic: str) -> dict:
    topic = (topic or "").strip()
    if not topic:
        return {"topic": "", "questions": []}

    questions = [
        f"What is {topic}?",
        f"How does {topic} work internally?",
        f"What are the advantages and disadvantages of {topic}?",
        f"Where is {topic} commonly applied in industry?",
        f"What are important terms/glossary related to {topic}?"
    ]
    return {"topic": topic, "questions": questions}
