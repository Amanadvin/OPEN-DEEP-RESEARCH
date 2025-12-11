# research_assistant.py  (IMPROVED & FOR STREAMLIT UI)
import os
import requests
import re
from typing import List, Dict, Iterable

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

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
# Returns dict with keys: content, sources, images
# ===============================================================
def web_search(query: str, max_results: int = 7) -> Dict:
    """
    Perform a general web search using Tavily (if TAVILY_API_KEY is set).
    Falls back to auto-generated text when Tavily is not available or on error.
    """
    if not TAVILY_API_KEY:
        return fallback_search(query)

    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    try:
        resp = requests.post(
            "https://api.tavily.com/v1/search",
            headers=headers,
            json={"q": query, "max_results": max_results, "include_images": True},
            timeout=20
        )
        if resp.status_code != 200:
            return fallback_search(query)

        data = resp.json()
        result_text_parts: List[str] = []
        sources: List[str] = []
        images: List[str] = []

        for item in data.get("results", []):
            content = item.get("content") or ""
            if content:
                result_text_parts.append(content)
            url = item.get("url")
            if url:
                sources.append(url)
            img = item.get("image_url")
            if img:
                images.append(img)

        return {
            "content": "\n\n".join(result_text_parts).strip(),
            "sources": list(dict.fromkeys(sources)),
            "images": list(dict.fromkeys(images))
        }

    except Exception:
        return fallback_search(query)


# ===============================================================
# Compatibility wrapper used by the Streamlit UI:
# searcher_agent receives a list of questions and returns a dict
# mapping question -> {content, sources, images}
# ===============================================================
def searcher_agent(questions: Iterable[str]) -> Dict[str, Dict]:
    answers = {}
    for q in questions:
        try:
            answers[q] = web_search(q)
        except Exception as e:
            answers[q] = {
                "content": f"Error performing web search: {e}",
                "sources": [],
                "images": []
            }
    return answers


# ===============================================================
# EXTRACT ACADEMIC / RESEARCH LINKS (DOI / PDF / ARXIV / PUBMED / PUBLISHERS)
# ===============================================================
def extract_academic_links(text: str) -> List[str]:
    """
    Extracts likely academic links from text:
    - explicit URLs containing keywords (ieee, springer, sciencedirect, arxiv, pubmed, doi, .pdf)
    - DOI patterns -> converted to https://doi.org/<doi>
    """
    if not text:
        return []

    academic_links = set()

    # find urls
    urls = re.findall(r'https?://[^\s,;)]+', text)
    for u in urls:
        low = u.lower()
        if any(key in low for key in [
            "ieee", "springer", "elsevier", "sciencedirect",
            "arxiv", ".pdf", "pubmed", "doi", "nature.com", "acm.org", "ncbi.nlm.nih.gov"
        ]):
            academic_links.add(u.rstrip(').,;'))

    # find DOIs and normalize
    dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', text)
    for d in dois:
        academic_links.add("https://doi.org/" + d)

    return list(academic_links)


# ===============================================================
# STRICT ACADEMIC RESEARCH MODE
# ===============================================================
def strict_research_agent(topic: str) -> Dict:
    """
    Return academic-only results for the given topic.
    Uses web_search with an academic-focused prompt and extracts DOIs/PDFs/arXiv links.
    Returns:
      {
        "topic": topic,
        "summary": <raw search content>,
        "papers": [...],          # list of links (primary)
        "references": [...],      # alias for compatibility
        "images": [...]
      }
    """
    prompt = (
        f"Return peer-reviewed academic research papers only about: '{topic}'. "
        f"Focus on IEEE, Springer, Elsevier, PubMed, arXiv, ACM and include DOI/arXiv/PDF links."
    )
    raw = web_search(prompt, max_results=10)
    content = raw.get("content", "")
    academic_links = extract_academic_links(content)
    # Also inspect the raw 'sources' returned by the search
    academic_links.extend([s for s in raw.get("sources", []) if any(k in s.lower() for k in ("ieee","arxiv","springer","doi","pubmed","acm","sciencedirect","nature"))])
    unique = list(dict.fromkeys(academic_links))
    return {
        "topic": topic,
        "summary": content,
        "papers": unique[:10],
        "references": unique[:10],
        "images": raw.get("images", [])
    }


# ===============================================================
# TOP-5 RESEARCH PAPER SEARCH
# ===============================================================
def top5_research_papers(topic: str) -> Dict:
    """
    Return top 5 academic links (PDF/DOI/arXiv) for a topic.
    Returns keys:
      - topic
      - top_5   (list)
      - top_5_papers (alias)
      - raw_text
    """
    prompt = (
        f"Find TOP research papers on '{topic}'. "
        f"Return only DOI, PDF, arXiv, PubMed, IEEE, Springer, ACM links and rank by relevance."
    )
    raw = web_search(prompt, max_results=10)
    academic_links = extract_academic_links(raw.get("content", ""))
    # include source urls that look academic
    academic_links.extend([s for s in raw.get("sources", []) if any(k in s.lower() for k in ("ieee","arxiv","springer","doi","pubmed","acm","sciencedirect","nature"))])
    unique = list(dict.fromkeys(academic_links))
    top5 = unique[:5]
    return {
        "topic": topic,
        "top_5": top5,
        "top_5_papers": top5,
        "raw_text": raw.get("content", "")
    }


# ===============================================================
# MERGED RESEARCH (WEB + ACADEMIC)
# ===============================================================
def merged_research_and_web(topic: str) -> Dict:
    """
    Run a combined search that returns both
      - web search results
      - extracted academic paper links
    Returns:
      {
        topic, summary, academic_papers, web_links, combined_sources
      }
    """
    prompt = (
        f"Provide complete research on '{topic}'. "
        f"Include both web results (articles/blogs) AND academic research papers (DOI/arXiv/PDF)."
    )
    raw = web_search(prompt, max_results=12)
    content = raw.get("content", "")
    web_links = _ensure_list(raw.get("sources", []))
    images = _ensure_list(raw.get("images", []))

    academic = extract_academic_links(content)
    # augment with any academic-looking web_links
    academic.extend([w for w in web_links if any(k in w.lower() for k in ("ieee","arxiv","springer","doi","pubmed","acm","sciencedirect","nature"))])

    combined = list(dict.fromkeys(academic + web_links))
    return {
        "topic": topic,
        "summary": content,
        "academic_papers": academic[:10],
        "web_links": web_links[:10],
        "combined_sources": combined[:15],
        "images": images
    }
