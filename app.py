# ============================================================
# OPEN DEEPRESEARCH AI — FULL MERGED APP.PY
# LM Studio + OpenAI Auto Fallback
# No Login | Sessions | Voice | PDF | Themes | Research
# ============================================================

import streamlit as st
import os, json, uuid, time, tempfile
from datetime import datetime
from pathlib import Path

# ---------- LLM CLIENTS ----------
from openai import OpenAI

# ---------- VOICE ----------
import speech_recognition as sr
from gtts import gTTS

# ---------- FILES ----------
from PyPDF2 import PdfReader

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Open DeepResearch AI",
    layout="wide"
)

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

# ============================================================
# LLM SETUP (LM STUDIO + OPENAI AUTO)
# ============================================================

def init_clients():
    openai_key = os.getenv("OPENAI_API_KEY")

    openai_client = None
    if openai_key:
        openai_client = OpenAI(api_key=openai_key)

    lm_client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        timeout=120
    )
    return lm_client, openai_client

LM_CLIENT, OPENAI_CLIENT = init_clients()

def generate_llm(prompt):
    # 1️⃣ Try LM Studio first
    try:
        res = LM_CLIENT.chat.completions.create(
            model="qwen2.5-7b-instruct",
            messages=[{"role":"user","content":prompt}]
        )
        return res.choices[0].message.content
    except Exception as lm_err:
        # 2️⃣ OpenAI fallback
        if OPENAI_CLIENT:
            try:
                res = OPENAI_CLIENT.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )
                return res.choices[0].message.content
            except Exception as oa_err:
                return f"❌ OpenAI Error: {oa_err}"
        return f"❌ LM Studio Error: {lm_err}"

# ============================================================
# SESSION HANDLING
# ============================================================

def new_session():
    sid = str(uuid.uuid4())
    path = os.path.join(SESSIONS_DIR, f"{sid}.json")
    with open(path, "w") as f:
        json.dump([], f)
    return sid

def load_session(sid):
    path = os.path.join(SESSIONS_DIR, f"{sid}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def save_session(sid, messages):
    path = os.path.join(SESSIONS_DIR, f"{sid}.json")
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)

def list_sessions():
    return [f.replace(".json","") for f in os.listdir(SESSIONS_DIR)]

# ============================================================
# SESSION STATE INIT
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = new_session()

if "messages" not in st.session_state:
    st.session_state.messages = load_session(st.session_state.session_id)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ============================================================
# THEMES
# ============================================================

LIGHT_CSS = """
<style>
.stApp { background:#ffffff; color:#0b1220; }
.user { background:#e3f2fd; padding:10px; border-radius:10px; text-align:right; }
.ai { background:#f5f5f5; padding:10px; border-radius:10px; }
</style>
"""

DARK_CSS = """
<style>
.stApp { background:#0d1117; color:#e6edf3; }
.user { background:#1e3a5f; padding:10px; border-radius:10px; text-align:right; }
.ai { background:#2d3748; padding:10px; border-radius:10px; }
</style>
"""

st.markdown(LIGHT_CSS if st.session_state.theme=="Light" else DARK_CSS, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🌗 Theme")
    st.session_state.theme = st.radio(
        "",
        ["Light","Dark"],
        index=0 if st.session_state.theme=="Light" else 1
    )

    st.divider()
    st.title("🧠 Open DeepResearch")

    mode = st.selectbox(
        "Mode",
        ["normal","deep research","fast summary","academic","code"]
    )

    st.divider()
    st.subheader("💬 Sessions")

    for sid in list_sessions():
        if st.button(sid[:8]):
            st.session_state.session_id = sid
            st.session_state.messages = load_session(sid)
            st.rerun()

    if st.button("➕ New Chat"):
        st.session_state.session_id = new_session()
        st.session_state.messages = []
        st.rerun()

# ============================================================
# MAIN CHAT UI
# ============================================================

st.title("🤖 Open DeepResearch AI")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai'>{msg['content']}</div>", unsafe_allow_html=True)

# ============================================================
# INPUTS
# ============================================================

col1, col2 = st.columns([4,1])

with col1:
    user_input = st.chat_input("Ask anything...")

with col2:
    if st.button("🎤 Speak"):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            st.info("Listening...")
            audio = r.listen(src)
        try:
            user_input = r.recognize_google(audio)
            st.success(user_input)
        except:
            st.error("Voice not clear")

# ============================================================
# FILE UPLOAD
# ============================================================

doc = st.file_uploader("Upload PDF / TXT", type=["pdf","txt"])

doc_text = ""
if doc:
    if doc.type == "application/pdf":
        reader = PdfReader(doc)
        for p in reader.pages:
            doc_text += p.extract_text() or ""
    else:
        doc_text = doc.read().decode()

# ============================================================
# PROCESS
# ============================================================

if user_input:
    if doc_text:
        prompt = f"Document:\n{doc_text}\n\nUser:\n{user_input}"
    else:
        prompt = user_input

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )

    with st.spinner("Thinking..."):
        try:
            answer = generate_llm(prompt)
        except Exception as e:
            answer = f"❌ Error: {e}"

    st.session_state.messages.append(
        {"role":"assistant","content":answer}
    )

    save_session(st.session_state.session_id, st.session_state.messages)

    # TTS
    try:
        tts = gTTS(answer)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(f.name)
        st.audio(open(f.name,"rb").read())
    except:
        pass

    st.rerun()

# ============================================================
# EXPORT
# ============================================================

st.divider()
if st.session_state.messages:
    txt = "\n\n".join(
        [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
    )
    st.download_button("⬇ Download Chat TXT", txt, file_name="chat.txt")
