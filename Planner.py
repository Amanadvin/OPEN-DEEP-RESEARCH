# -------------------------------------------------
# PLANNER AGENT — Creates 6 research sub-questions
# -------------------------------------------------

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    timeout=180
)

def planner_agent(topic: str):
    prompt = f"""
You are a planning agent.

Generate 6 important research sub-questions for the topic:
**{topic}**

Questions must cover:
- Definition
- Types
- Advantages & disadvantages
- Importance
- Important terms
- Working / How it works
- Features
- Applications
- Real-world examples

Return ONLY the list of questions.
"""
    response = client.chat.completions.create(
        model="qwen2.5-7b-instruct-1m-q4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.split("\n")
