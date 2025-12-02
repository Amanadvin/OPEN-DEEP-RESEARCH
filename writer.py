# -------------------------------------------------
# WRITER AGENT — Generates final research paper
# -------------------------------------------------

from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    timeout=180
)

def writer_agent(topic: str, qa_pairs: dict):

    prompt = f"""
You are an expert AI research writer.

Write a complete research document on:
**{topic}**

Use the following retrieved information:
{qa_pairs}

Follow this structure exactly:

📌 1. Definition
📌 2. Explanation (Detailed)
📌 3. TYPES (Detailed)
📌 4. Key Features
📌 5. Pros
📌 6. Cons
📌 7. Applications / Use Cases
📌 8. Architecture / Flow Diagram (ASCII)
📌 9. Examples
📌 10. Glossary
📌 11. Final Summary
"""

    response = client.chat.completions.create(
        model="qwen2.5-7b-instruct-1m-q4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------------------------------------------------
# PDF GENERATOR
# -------------------------------------------------
def generate_pdf(text, filename="research_output.pdf"):

    styles = getSampleStyleSheet()
    story = []
    doc = SimpleDocTemplate(filename, pagesize=A4)

    for line in text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return filename
