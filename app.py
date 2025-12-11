# app.py — Open DeepResearch AI (Streamlit EUI)
# Mode-only logic (Option B): UI mode fully controls output behavior

import streamlit as st
import os
import json
import tempfile
import wave
import time
from datetime import datetime
from pathlib import Path

from pipeline import run_langgraph_pipeline
from gtts import gTTS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from vosk import Model, KaldiRecognizer
from PyPDF2 import PdfReader
from streamlit_mic_recorder import mic_recorder

# Import research & writer modules
from research_assistant import (
    searcher_agent,
    strict_research_agent,
    top5_research_papers,
    merged_research_and_web,
    web_search
)
from writer import writer_agent, generate_pdf as writer_generate_pdf

# --------------------------- CONFIG & PATHS ---------------------------
SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

LOGO_PATH = "logo.png"
VOSK_MODEL_PATH = "vosk-model"

# --------------------------- THEME CSS ---------------------------
LIGHT_CSS = """
<style>
body, .stApp { background-color: #ffffff !important; color: #0b1220 !important; }
.stMarkdown, .stTextInput, .stButton, .stSelectbox, .stRadio, .stTextArea { color: #0b1220 !important; }
.chat-container { max-width: 800px; margin: 0 auto; padding: 20px; }
.chat-message { margin-bottom: 20px; padding: 10px; border-radius: 10px; }
.user-message { background-color: #e3f2fd; text-align: right; }
.assistant-message { background-color: #f5f5f5; }
</style>
"""

DARK_CSS = """
<style>
body, .stApp { background-color: #0d1117 !important; color: #e6edf3 !important; }
.stMarkdown, .stTextInput, .stButton, .stSelectbox, .stRadio, .stTextArea { color: #e6edf3 !important; }
.chat-container { max-width: 800px; margin: 0 auto; padding: 20px; }
.chat-message { margin-bottom: 20px; padding: 10px; border-radius: 10px; }
.user-message { background-color: #1e3a5f; text-align: right; }
.assistant-message { background-color: #2d3748; }
</style>
"""

# --------------------------- STREAMLIT PAGE ---------------------------
st.set_page_config(
    page_title="OPEN DEEPRESEARCH A.I",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------- SESSION STORAGE UTILITIES ---------------------------
def _session_path(filename: str) -> str:
    return os.path.join(SESSIONS_DIR, filename)

def list_session_files():
    return [f for f in sorted(os.listdir(SESSIONS_DIR), reverse=True) if f.endswith(".json")]

def load_session_file(filename: str):
    path = _session_path(filename)
    if not os.path.exists(path):
        return {"title": "New Chat", "created": datetime.now().isoformat(), "messages": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"title": "New Chat", "created": datetime.now().isoformat(), "messages": []}

def save_session_file(filename: str, data: dict):
    path = _session_path(filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

def create_new_session_file():
    session_id = int(datetime.now().timestamp())
    filename = f"session_{session_id}.json"
    data = {"title": "New Chat", "created": datetime.now().isoformat(), "messages": []}
    save_session_file(filename, data)
    return filename

def delete_session_file(filename: str):
    path = _session_path(filename)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

# --------------------------- VOSK TRANSCRIPTION ---------------------------
def transcribe_audio_offline(wav_path):
    try:
        if not os.path.exists(VOSK_MODEL_PATH):
            st.warning("Vosk model not found. Voice disabled.")
            return ""
        model = Model(VOSK_MODEL_PATH)
        rec = KaldiRecognizer(model, 16000)
        with wave.open(wav_path, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
        return json.loads(rec.FinalResult()).get("text", "")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return ""

# --------------------------- DOCUMENT TEXT EXTRACTION ---------------------------
def extract_text_from_file(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file.type == "text/plain":
        return str(file.read(), "utf-8")
    else:
        return "Unsupported file type."

# --------------------------- TEXT SUMMARIZATION/TRUNCATION ---------------------------
def summarize_or_truncate_text(text, max_tokens=3000):
    words = text.split()
    if len(words) > max_tokens:
        truncated = " ".join(words[:max_tokens])
        return truncated + "\n\n[Text truncated due to length. Please provide a shorter document or specify a summary request.]"
    return text

# --------------------------- TTS ---------------------------
def do_tts(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(f.name)
    return f.name

# --------------------------- PDF EXPORT ---------------------------
def create_pdf(text, title):
    from io import BytesIO
    buffer = BytesIO()
    safe_title = (title or "session").replace(" ", "_")[:40]
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"{title}")
    y -= 30
    c.setFont("Helvetica", 10)
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
        c.drawString(40, y, line)
        y -= 14
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# --------------------------- MEMORY LOG ---------------------------
def append_memory_log(query, answer):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\nQ: {query}\nA: {answer}\n")

# --------------------------- SESSION STATE INIT ---------------------------
if "current_session_file" not in st.session_state:
    files = list_session_files()
    st.session_state.current_session_file = files[0] if files else create_new_session_file()

if "session_data" not in st.session_state:
    st.session_state.session_data = load_session_file(st.session_state.current_session_file)

if "stats" not in st.session_state:
    st.session_state.stats = {"total": 0, "today": 0, "last": ""}

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "uploaded_doc_text" not in st.session_state:
    st.session_state.uploaded_doc_text = ""

# --------------------------- SIDEBAR ---------------------------
with st.sidebar:
    st.markdown("### 🌗 Theme Mode")
    st.session_state.theme = st.radio("", ["Light", "Dark"], index=0 if st.session_state.theme=="Light" else 1)
    st.markdown(LIGHT_CSS if st.session_state.theme=="Light" else DARK_CSS, unsafe_allow_html=True)

    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=140)
    st.title("OPEN DEEPRESEARCH")

    mode = st.selectbox("Mode", ["normal", "deep research", "fast summary", "academic", "code", "web search", "research papers", "hybrid search"], index=0)
    tts_lang = st.selectbox("Voice", ["en", "hi", "fr", "es"])

    st.subheader("💬 Sessions")
    st.markdown(f"**Current:** {st.session_state.current_session_file}")
    cols = st.columns([1,1,1])
    if cols[0].button("➕ New Chat"):
        st.session_state.current_session_file = create_new_session_file()
        st.session_state.session_data = load_session_file(st.session_state.current_session_file)
        st.session_state.uploaded_doc_text = ""
        st.experimental_rerun()
    if cols[1].button("💾 Save"):
        save_session_file(st.session_state.current_session_file, st.session_state.session_data)
        st.success("Session saved.")
    if cols[2].button("🗑️ Delete"):
        delete_session_file(st.session_state.current_session_file)
        files = list_session_files()
        st.session_state.current_session_file = files[0] if files else create_new_session_file()
        st.session_state.session_data = load_session_file(st.session_state.current_session_file)
        st.session_state.uploaded_doc_text = ""
        st.rerun()

    st.divider()
    st.markdown("**Previous Sessions**")
    files = list_session_files()
    if files:
        selected = st.selectbox("Load a session", ["-- choose --"] + files)
        if selected and selected != "-- choose --":
            st.session_state.current_session_file = selected
            st.session_state.session_data = load_session_file(selected)
            st.session_state.uploaded_doc_text = ""
            st.rerun()
    else:
        st.write("_No sessions found_")

    st.divider()
    st.subheader("📁 Export Current Session")
    export_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.session_data.get("messages", [])])
    export_txt_bytes = export_txt.encode('utf-8')
    st.download_button("Download TXT", export_txt_bytes, file_name=f"{st.session_state.session_data.get('title','session')}.txt", mime="text/plain")
    export_pdf_bytes = create_pdf(export_txt, st.session_state.session_data.get("title", "session"))
    pdf_filename = f"{st.session_state.session_data.get('title','session')}.pdf"
    st.download_button("Download PDF", export_pdf_bytes, file_name=pdf_filename, mime="application/pdf")

# --------------------------- MAIN UI ---------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.title("🤖 Open DeepResearch AI")

for msg in st.session_state.session_data.get("messages", []):
    role_class = "user-message" if msg.get("role") == "user" else "assistant-message"
    st.markdown(f'<div class="chat-message {role_class}">{msg.get("content","")}</div>', unsafe_allow_html=True)
    if msg.get("sources"):
        with st.expander("🔍 Sources & Details"):
            st.markdown(msg.get("sources"))

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------- INPUTS ---------------------------
st.divider()
st.caption("Optional Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🎤 Voice Input")
    audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key="recorder")
    if audio:
        st.success("Audio recorded. Transcribing...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio['bytes'])
            tmp_path = tmp_file.name
        transcribed_text = transcribe_audio_offline(tmp_path)
        final_input = transcribed_text if transcribed_text else ""
with col2:
    pasted_text = st.text_area("Paste text", height=60)
with col3:
    doc_file = st.file_uploader("Upload a document (PDF/TXT)", type=["pdf", "txt"])
    if doc_file and not st.session_state.uploaded_doc_text:
        st.session_state.uploaded_doc_text = extract_text_from_file(doc_file)
        st.success("Document uploaded successfully. Enter your prompt to process it.")

user_query = st.chat_input("Ask me anything...")

final_input = ""
if 'transcribed_text' in locals() and transcribed_text:
    final_input = transcribed_text
elif pasted_text and pasted_text.strip():
    final_input = pasted_text.strip()
elif user_query:
    if st.session_state.uploaded_doc_text:
        processed_doc = summarize_or_truncate_text(st.session_state.uploaded_doc_text)
        final_input = f"Document content:\n{processed_doc}\n\nUser instruction: {user_query}"
    else:
        final_input = user_query.strip()

# --------------------------- PROCESS & PIPELINE ---------------------------
if final_input:
    st.session_state.session_data.setdefault("messages", []).append({"role":"user","content":final_input})
    if st.session_state.session_data.get("title","New Chat") in (None,"","New Chat"):
        st.session_state.session_data["title"] = final_input[:60]

    st.markdown(f'<div class="chat-message user-message">{final_input}</div>', unsafe_allow_html=True)
    placeholder = st.empty()

    final_answer = ""
    detail_text = ""
    result = None

    with st.spinner("Processing..."):
        try:
            # ---------------- Mode-only logic mapping ----------------
            if mode == "normal" or mode == "code":
                result = run_langgraph_pipeline(final_input, mode=mode)
                final_answer = result.get("final_text","") if result else "No response."
                if result and isinstance(result.get("answers"), dict):
                    for q, info in result["answers"].items():
                        detail_text += f"### {q}\n{info.get('content','')}\n\n"
                        if info.get("sources"):
                            detail_text += "Sources:\n" + "\n".join(info["sources"]) + "\n\n"
            elif mode == "deep research":
                merged = merged_research_and_web(final_input)
                final_answer = writer_agent(final_input, merged)
                if merged.get("combined_sources"):
                    detail_text = "\n".join([f"- {s}" for s in merged["combined_sources"]])
            elif mode == "fast summary":
                web = searcher_agent([final_input]).get(final_input,{})
                final_answer = (web.get("content") or "No results found.")[:1500]
                if web.get("sources"):
                    detail_text = "\n".join([f"- {s}" for s in web["sources"]])
            elif mode == "academic":
                top = top5_research_papers(final_input)
                papers = top.get("top_5") or []
                final_answer = "\n".join([f"{i+1}. {p}" for i,p in enumerate(papers)]) if papers else "No papers found."
                detail_text = "\n".join([f"- {p}" for p in papers])
            elif mode == "web search":
                web = searcher_agent([final_input]).get(final_input,{})
                final_answer = web.get("content","No web results found.")
                if web.get("sources"):
                    detail_text = "\n".join([f"- {s}" for s in web["sources"]])
            elif mode == "research papers":
                research = strict_research_agent(final_input)
                final_answer = research.get("summary","No summary found.")
                refs = research.get("references",[])
                detail_text = "\n".join([f"- {r}" for r in refs])
            elif mode == "hybrid search":
                merged = merged_research_and_web(final_input)
                final_answer = merged.get("summary","No results.")
                academic = merged.get("academic_papers",[])
                web_links = merged.get("web_links",[])
                detail_text = "\n".join([f"- {a}" for a in academic] + [f"- {w}" for w in web_links])
            else:
                final_answer = "Mode not supported."

        except Exception as e:
            final_answer = f"Error: {e}"
            detail_text = ""

    # Typing animation
    typing_text = ""
    for char in final_answer:
        typing_text += char
        placeholder.markdown(typing_text + "▌")
        time.sleep(0.01)
    placeholder.markdown(final_answer)

    if detail_text:
        with st.expander("🔍 Sources & Details"):
            st.markdown(detail_text)

    # TTS
    try:
        audio_path = do_tts(final_answer, lang=tts_lang)
        st.audio(open(audio_path,"rb").read())
    except:
        pass

    # Downloads
    txt_name = f"{st.session_state.session_data.get('title','session')[:30].replace(' ','_')}.txt"
    txt_bytes = final_answer.encode('utf-8')
    st.download_button("Download TXT (response)", txt_bytes, file_name=txt_name, mime="text/plain")

    # Writer Agent PDF
    if mode=="deep research":
        try:
            pdf_name = writer_generate_pdf(final_answer, filename=f"{st.session_state.session_data.get('title','research')[:40].replace(' ','_')}.pdf")
            with open(pdf_name,"rb") as pf:
                st.download_button("Download Research PDF", pf, file_name=pdf_name)
        except:
            pdf_bytes = create_pdf(final_answer, st.session_state.session_data.get("title","session"))
            pdf_name = f"{st.session_state.session_data.get('title','session')}.pdf"
            st.download_button("Download PDF (response)", pdf_bytes, file_name=pdf_name, mime="application/pdf")
    else:
        pdf_bytes = create_pdf(final_answer, st.session_state.session_data.get("title","session"))
        pdf_name = f"{st.session_state.session_data.get('title','session')}.pdf"
        st.download_button("Download PDF (response)", pdf_bytes, file_name=pdf_name, mime="application/pdf")

    st.session_state.session_data.setdefault("messages",[]).append({"role":"assistant","content":final_answer,"sources":detail_text})
    st.session_state.stats["total"] +=1
    st.session_state.stats["today"] +=1
    st.session_state.stats["last"] = final_input
    append_memory_log(final_input, final_answer)
    save_session_file(st.session_state.current_session_file, st.session_state.session_data)

    if st.button("Refresh"):
        st.rerun()
