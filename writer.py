# -------------------------------------------------
# WRITER AGENT — Generates research papers or direct answers
# -------------------------------------------------

from openai import OpenAI, RateLimitError
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Local LM Studio Client
local_client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    timeout=180
)

# OpenAI Client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# Helper: Decide if query is simple/factual
# ---------------------------
def is_simple_question(query: str) -> bool:
    """
    Returns True if the query is a short factual question.
    Example: 'Who is the current Prime Minister of India?'
    """
    simple_keywords = ["who", "what", "when", "where", "how many", "how much", "current"]
    # Very basic heuristic: short length + simple keywords
    if len(query.split()) <= 12 and any(kw in query.lower() for kw in simple_keywords):
        return True
    return False

# ---------------------------
# WRITER AGENT FUNCTION
# ---------------------------
def writer_agent(topic: str, qa_pairs: dict = None, use_openai: bool = False, mode: str = "normal") -> str:
    """
    Generates structured research paper OR a direct answer depending on mode.
    
    mode: 'normal', 'deep_research', 'academic', 'factual'
    """

    # ---------------------------
    # 1️⃣ Simple factual answer mode
    # ---------------------------
    if mode == "factual" or is_simple_question(topic):
        prompt = f"Answer concisely in 1-2 sentences:\n\nQuestion: {topic}"
    else:
        # ---------------------------
        # 2️⃣ Full research paper mode
        # ---------------------------
        prompt = f"""
You are an expert AI research writer.

Write a complete research document on:
**{topic}**

Use the following retrieved information:
{qa_pairs or {}}

Follow this structure exactly:

1. Definition
2. Explanation (Detailed)
3. TYPES (Detailed)
4. Key Features
5. Pros
6. Cons
7. Applications / Use Cases
8. Architecture / Flow Diagram (ASCII)
9. Examples
10. Glossary
11. References
12. Final Summary
"""

    # ---------------------------
    # Generate base text using LM Studio
    # ---------------------------
    try:
        response = local_client.chat.completions.create(
            model="qwen2.5-7b-instruct-1m-q4",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content
    except Exception as e:
        text = f"⚠️ LM Studio generation failed: {str(e)}"

    # ---------------------------
    # Optional: Polish using OpenAI GPT
    # ---------------------------
    if use_openai and not is_simple_question(topic):
        polish_prompt = f"Improve clarity, structure, and readability of this research document:\n\n{text}"
        try:
            polish_res = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": polish_prompt}]
            )
            text = polish_res.choices[0].message.content
        except RateLimitError:
            text += (
                "\n\n⚠️ OpenAI API quota finished. Using raw LM Studio output."
            )
        except Exception as e:
            text += f"\n\n⚠️ OpenAI polishing failed: {str(e)}"

    # ---------------------------
    # Cleanup: Remove redundant newlines
    # ---------------------------
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

# ---------------------------
# PDF GENERATOR
# ---------------------------
def generate_pdf(text: str, filename: str = "research_output.pdf") -> str:
    """
    Generates a PDF from the provided text. Returns PDF filename.
    """
    styles = getSampleStyleSheet()
    story = []
    doc = SimpleDocTemplate(filename, pagesize=A4)

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return filename
