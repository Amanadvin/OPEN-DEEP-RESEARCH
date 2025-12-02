# -------------------------------------------------
# LANGGRAPH PIPELINE — Complete Multi-Agent Research System
# With: Research Paper Links, Memory, Structured Reports, History Section
# -------------------------------------------------

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from Planner import planner_agent
from research_assistant import searcher_agent
from writer import writer_agent, generate_pdf
import json
import os

# =====================================================
# MEMORY STORAGE (JSON File)
# =====================================================

MEMORY_FILE = "session_memory.json"

def load_memory():
    """Loads memory from a JSON file if present."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"history": []}

def save_memory(memory):
    """Saves memory back to the file."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

session_memory = load_memory()

# =====================================================
# GRAPH STATE
# =====================================================

class ResearchState(TypedDict):
    topic: str
    questions: List[str]
    results: Dict[str, Dict[str, str]]  # includes answer + link
    final_output: str

# =====================================================
# AGENT WRAPPERS
# =====================================================

def planner_node(state: ResearchState):
    qs = planner_agent(state["topic"])
    return {"questions": qs}

def searcher_node(state: ResearchState):
    all_results = {}
    for q in state["questions"]:
        if q.strip():
            search_output = searcher_agent(q)
            all_results[q] = {
                "answer": search_output.get("answer", ""),
                "source": search_output.get("source", "No link found")
            }
    return {"results": all_results}

def writer_node(state: ResearchState):
    structured_report = generate_structured_report(
        state["topic"],
        state["results"],
        session_memory
    )
    final_text = writer_agent(state["topic"], state["results"])

    # Save to memory
    session_memory["history"].append({
        "topic": state["topic"],
        "questions": state["questions"],
        "results": state["results"],
        "report": structured_report
    })
    save_memory(session_memory)

    return {"final_output": structured_report + "\n\n" + final_text}

# =====================================================
# STRUCTURED REPORT GENERATOR WITH HISTORY
# =====================================================

def generate_structured_report(topic, results, session_memory=None):
    report = []
    if session_memory is None:
        session_memory = {"history": []}

    report.append("============================================")
    report.append(f"📘 STRUCTURED RESEARCH REPORT ON: {topic}")
    report.append("============================================\n")

    report.append("🔹 **Executive Summary**")
    report.append(f"This report provides a researched, multi-step analysis on **{topic}**.\n")

    report.append("🔹 **Research Questions & Findings**\n")
    for q, data in results.items():
        report.append(f"### 🔍 {q}")
        report.append(f"**Answer:** {data['answer']}")
        report.append(f"**Research Paper/Source:** {data['source']}\n")

    report.append("🔹 **Conclusion**")
    report.append("This structured report is auto-generated through a multi-agent LLM workflow.\n")

    # -------------------------
    # History Section
    # -------------------------
    if session_memory.get("history"):
        report.append("\n============================================")
        report.append("📜 PAST SEARCH HISTORY")
        report.append("============================================\n")
        for idx, entry in enumerate(session_memory["history"], start=1):
            report.append(f"### 📝 History Entry {idx}")
            report.append(f"**Topic:** {entry['topic']}")
            report.append("**Questions Asked:**")
            for q in entry["questions"]:
                report.append(f"- {q}")
            report.append("**Results:**")
            for q, data in entry["results"].items():
                report.append(f"- **{q}**")
                report.append(f"  - Answer: {data['answer']}")
                report.append(f"  - Source: {data['source']}")
            report.append("\n--------------------------------------------")

    return "\n".join(report)

# =====================================================
# BUILD THE LANGGRAPH PIPELINE
# =====================================================

graph = StateGraph(ResearchState)

graph.add_node("planner", planner_node)
graph.add_node("searcher", searcher_node)
graph.add_node("writer", writer_node)

graph.set_entry_point("planner")

graph.add_edge("planner", "searcher")
graph.add_edge("searcher", "writer")
graph.add_edge("writer", END)

app = graph.compile()

# =====================================================
# MAIN RUN FUNCTION
# =====================================================

def run_research():
    topic = input("\nEnter your research topic: ")

    print("\n🚀 Running Full Research Pipeline...\n")

    result = app.invoke({"topic": topic})
    final_text = result["final_output"]

    print("\n================= FINAL OUTPUT =================\n")
    print(final_text)
    print("\n================================================\n")

    print("📄 Generating PDF...")
    filename = generate_pdf(final_text)

    print(f"✅ PDF Saved: {filename}")
    print(f"📥 PDF Link: file://{filename}")

    print("\n🧠 Memory Updated Successfully!")

if __name__ == "__main__":
    run_research()
