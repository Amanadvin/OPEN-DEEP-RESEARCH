# research_assistant.py  (IMPROVED & FOR STREAMLIT UI)
import os
import requests
import re
from typing import List, Dict, Iterable
from urllib.parse import quote_plus
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Local LM Studio Client
local_client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    timeout=180
)

# -----------------------------
# Small helper: safe listify
# -----------------------------
def _ensure_list(x) -> list:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, (set, tuple)):
        return list(x)
    return [x]


# ===============================================================
# FALLBACK (when Tavily not configured or on errors)
# ===============================================================
def fallback_search(question: str) -> Dict:
    return {
        "content": f"Auto-generated explanation for: {question}",
        "sources": [],
        "images": []
    }


# ===============================================================
# GENERIC WEB SEARCH (TAVILY wrapper)
# ===============================================================
def web_search(query: str, max_results: int = 7) -> Dict:
    if not TAVILY_API_KEY:
        return fallback_search(query)

    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json={"query": query, "max_results": max_results},
            timeout=20
        )
        if resp.status_code != 200:
            return fallback_search(query)

        data = resp.json()
        content_parts, sources = [], []

        for item in data.get("results", []):
            if item.get("content"):
                content_parts.append(item["content"])
            if item.get("url"):
                sources.append(item["url"])

        return {
            "content": "\n\n".join(content_parts).strip(),
            "sources": list(dict.fromkeys(sources)),
            "images": data.get("images", [])
        }

    except Exception:
        return fallback_search(query)


# ===============================================================
# SEARCHER AGENT
# ===============================================================
def searcher_agent(questions: Iterable[str]) -> Dict[str, Dict]:
    answers = {}
    for q in questions:
        try:
            response = local_client.chat.completions.create(
                model="qwen2.5-7b-instruct-1m-q4",
                messages=[{"role": "user", "content": f"Provide detailed information and answer to: {q}"}]
            )
            answers[q] = {
                "content": response.choices[0].message.content,
                "sources": [],
                "images": []
            }
        except Exception as e:
            answers[q] = {"content": f"Error: {e}", "sources": [], "images": []}
    return answers


# ===============================================================
# EXTRACT ACADEMIC LINKS (UPDATED)
# ===============================================================
def extract_academic_links(text: str) -> List[str]:
    """
    Extract academic links and convert DOI → Google Scholar.
    Prioritizes free PDFs and trusted academic sources.
    """
    if not text:
        return []

    links = set()

    # Academic URL patterns
    urls = re.findall(r'https?://[^\s,;)]+', text)
    for u in urls:
        clean = u.rstrip(').,;')
        low = clean.lower()
        if any(k in low for k in [
            "arxiv.org",
            "ieee",
            "springer",
            "sciencedirect",
            "nature.com",
            "pubmed",
            "ncbi.nlm.nih.gov",
            "acm.org",
            "researchgate",
            ".pdf"
        ]):
            links.add(clean)

    # DOI → Google Scholar
    dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', text)
    for doi in dois:
        scholar = "https://scholar.google.com/scholar?q=" + quote_plus(doi)
        links.add(scholar)

    # Rank: PDFs first
    sorted_links = sorted(
        links,
        key=lambda x: (".pdf" not in x.lower(), "arxiv" not in x.lower())
    )

    return sorted_links


# ===============================================================
# STRICT ACADEMIC RESEARCH MODE
# ===============================================================
def strict_research_agent(topic: str) -> Dict:
    prompt = (
        f"Provide an academic research summary on '{topic}'. "
        "List peer-reviewed papers with DOI, arXiv, or PDF links "
        "(IEEE, Springer, Elsevier, PubMed, ACM)."
    )
    try:
        response = local_client.chat.completions.create(
            model="qwen2.5-7b-instruct-1m-q4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        papers = extract_academic_links(content)
        return {
            "topic": topic,
            "summary": content,
            "papers": papers[:10],
            "references": papers[:10],
            "images": []
        }
    except Exception as e:
        return {"topic": topic, "summary": f"Error: {e}", "papers": [], "references": [], "images": []}


# ===============================================================
# TOP-5 RESEARCH PAPERS
# ===============================================================
def top5_research_papers(topic: str) -> Dict:
    prompt = (
        f"Find top 5 academic research papers on '{topic}'. "
        "Return only titles and links (DOI, arXiv, PDF)."
    )
    try:
        response = local_client.chat.completions.create(
            model="qwen2.5-7b-instruct-1m-q4",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content
        links = extract_academic_links(raw)
        return {
            "topic": topic,
            "top_5": links[:5],
            "top_5_papers": links[:5],
            "raw_text": raw
        }
    except Exception as e:
        return {"topic": topic, "top_5": [], "top_5_papers": [], "raw_text": f"Error: {e}"}


# ===============================================================
# MERGED RESEARCH (WEB + ACADEMIC)
# ===============================================================
def merged_research_and_web(topic: str) -> Dict:
    prompt = (
        f"Provide complete research on '{topic}'. "
        "Include academic papers and general web articles with links."
    )
    try:
        response = local_client.chat.completions.create(
            model="qwen2.5-7b-instruct-1m-q4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        links = extract_academic_links(content)
        academic = [l for l in links if any(k in l.lower() for k in ("arxiv", "ieee", "springer", "acm", "pubmed", "scholar"))]

        return {
            "topic": topic,
            "summary": content,
            "academic_papers": academic[:10],
            "web_links": links[:10],
            "combined_sources": list(dict.fromkeys(academic + links))[:15],
            "images": []
        }
    except Exception as e:
        return {
            "topic": topic,
            "summary": f"Error: {e}",
            "academic_papers": [],
            "web_links": [],
            "combined_sources": [],
            "images": []
        }
