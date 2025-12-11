# -------------------------------------------------
# pipeline.py  — Complete LangGraph Pipeline (Fixed)
# -------------------------------------------------

from Planner import planner_agent
from research_assistant import searcher_agent
from writer import writer_agent


def run_langgraph_pipeline(
    user_query: str,
    mode: str = "normal",
    use_openai_polish: bool = False
):
    """
    Main LangGraph Pipeline
    mode = normal / deep research / summary / academic / code
    """

    print(f"[Pipeline Mode] {mode}")

    # 1️⃣ STEP 1 — PLAN
    plan = planner_agent(user_query)

    # planner_agent must return {'topic': str, 'questions': list}
    topic = plan.get("topic", user_query)
    questions = plan.get("questions", [])

    # 2️⃣ STEP 2 — SEARCH / RESEARCH
    # searcher_agent must return:
    # { question: { 'content': ..., 'sources': ..., 'images': ... } }
    answers = searcher_agent(questions)

    # 3️⃣ STEP 3 — WRITE FINAL RESULT (with optional OpenAI polishing)
    final_text = writer_agent(
        topic=topic,
        qa_pairs=answers,
        use_openai=use_openai_polish
    )

    # 4️⃣ STEP 4 — RETURN FULL RESULT STRUCTURE
    return {
        "topic": topic,
        "answers": answers,
        "final_text": final_text,
        "mode": mode
    }
