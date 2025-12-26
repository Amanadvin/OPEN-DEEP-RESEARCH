# Open Deep Research


## 1. Project Title
**Open Deep Research** – A Multi-Agent AI System for Research-Oriented Question Answering


The project works like a smart human researcher. First, it understands the user’s question and breaks it into smaller parts. Then it searches the internet for reliable information, studies the collected data, and finally writes a clear and structured research report.

---
**The system uses multiple AI agents:**

- A Planner Agent decides what to research.

- A Searcher Agent finds useful information from the web.

- A Writer Agent summarizes and explains the findings in simple language.

All agents are connected using an agent workflow system, allowing smooth coordination. The project can also remember previous research sessions, so users can continue their work later.

OpenDeepResearcher is built using Python, LangGraph, LangChain, local LLMs (like LM Studio), and the Tavily search API. It is useful for students, researchers, and anyone who wants fast, organized, and reliable research output.


---

## 2. Project Overview 

OpenDeepResearcher is an AI-powered research assistant designed to autonomously perform deep, multi-step research on complex topics using Large Language Models (LLMs) and agentic workflows.

🔍 Problem It Solves

Manual research is time-consuming

Information is scattered across multiple sources

Difficult to plan, retrieve, analyze, and summarize efficiently

## Main Objective 

To automate the entire research pipeline by simulating how a human researcher:

- Plans research

- Searches credible sources

- Synthesizes findings

- Produces structured research reports

This results in high-quality, multi-perspective research outputs with minimal human effort.
---
## 3. Project Objective (Explained Clearly)

**The main goal of OpenDeepResearcher is to:**

- Reduce manual research effort

- Automate complex topic exploration

- Generate high-quality, structured research reports

- Combine web knowledge + academic knowledge

- Work cost-effectively using local LLMs

- Why this project is important

- Traditional research requires:

- Searching many websites

- Reading long articles

- Summarizing manually

- This system does all of that automatically, just like a skilled human researcher.


Agentic AI Research Assistant

OpenDeepResearcher is an AI-powered research assistant that automatically plans, searches, analyzes, and writes structured research reports. It uses multiple AI agents and local or hosted LLMs to mimic how a human researcher works.

---

## 4. Software and Hardware Dependencies

### Software Dependencies

**Programming Language**
- Python 3.10+

**Core Libraries & Frameworks**

- LangGraph – Multi-agent workflow orchestration

- LangChain – LLM integration, memory handling, tools

- Streamlit / Flask – User Interface (optional)

**APIs & Tools**

- Tavily API – Web search & real-time data retrieval

- LM Studio / Ollama – Local LLM inference

- OpenAI-compatible API Interface

**Models Used**

- Qwen2.5-7B-Instruct (or any instruction-tuned LLM)

- Environment & Tooling

- pip, venv

- Git for version control

### Hardware Dependencies

The system is optimized to run on a standard student laptop:
- Processor: Intel i5 core
- RAM: Minimum 8 GB
- Storage: At least 5 GB free space
- GPU: Not required
- Operating System: Windows 11

---

---

## 5. High-Level Architecture

The architecture of Open Deep Research follows a layered multi-agent design.

![Open Deep Research Architecture](https://github.com/LakshanLikhitM/OPEN-DEEP-RESEARCH/blob/main/architecture.png)

### Architecture Description

- The Streamlit interface handles all user interactions.
- A session memory layer maintains conversation context.
- The Planner Agent analyzes user queries and structures research steps.
- The Searcher Agent retrieves information from trusted academic sources.
- The Writer Agent synthesizes research into a clear final response.
- Chat history is stored locally and can be reused within the session.

---

🔄 Overall Workflow (Human-like Research Flow)
User Query
   ↓
Planner Agent (creates research questions)
   ↓
Searcher Agent (collects information)
   ↓
Writer Agent (analyzes & writes report)
   ↓
Final Structured Research Output (PDF / Text / Voice)

⚙️ Core Components
🔹 Planner Agent

Understands the research query

Breaks it into smaller sub-questions

Creates a structured research roadmap

🔹 Searcher Agent

Uses Tavily API for real-time web search

Collects relevant and up-to-date information

Filters unnecessary or duplicate data

🔹 Writer Agent

Uses an LLM to analyze retrieved content

Summarizes information clearly

Generates structured research sections

🔹 Execution Graph (LangGraph)

Controls agent execution order

Manages data flow between agents

Ensures reliable end-to-end workflow

🔹 Memory System (Optional)

Stores research sessions

Enables multi-step and iterative research

Improves continuity across prompts

🧪 Tech Stack

Language: Python 3.10+

Agent Framework: LangGraph

LLM Orchestration: LangChain

LLMs: LM Studio / Ollama / OpenAI-compatible APIs

Search API: Tavily

UI: Streamlit

Version Control: Git

Containerization: Docker

🚀 How to Run (Local Setup)
1️⃣ Clone the Repository
git clone https://github.com/your-username/OpenDeepResearcher.git
cd OpenDeepResearcher

2️⃣ Create Virtual Environment
python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Linux / macOS

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file:

TAVILY_API_KEY=your_tavily_api_key
OPENAI_API_KEY=lm-studio
OPENAI_BASE_URL=http://localhost:1234/v1

5️⃣ Start Local LLM

Open LM Studio

Load a model (e.g., Qwen2.5-7B-Instruct)

Start the local server

6️⃣ Run the Application
streamlit run app.py


Open browser:

http://localhost:8501

🐳 Docker Setup
🔹 Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

🔹 Build Docker Image
docker build -t opendeepresearcher .

🔹 Run Docker Container
docker run -p 8501:8501 --env-file .env opendeepresearcher

📊 Evaluation

The project is evaluated based on the following criteria:

Correctness

Accurate planning and topic decomposition

Relevant search results

Agent Coordination

Smooth execution across Planner, Searcher, and Writer

Output Quality

Clarity, structure, and completeness of reports

Performance

Efficient response time

Minimal redundancy

Usability

Easy-to-use UI

Clear research flow

Milestone-based evaluations ensure steady progress and reliability.

🔮 Future Scope

🔹 Add citation formatting (APA / IEEE)

🔹 PDF & DOCX report export

🔹 Multi-language research support

🔹 Academic paper-level synthesis

🔹 Multi-search engine integration

🔹 Reinforcement learning for agent optimization

🔹 Collaborative multi-user research

🔹 Knowledge graph–based memory system

👥 Target Users

Students

Researchers

Educators

Developers

Content writers

✅ Key Benefits

Fully automated research workflow

Human-like agent behavior

Local LLM support (privacy + low cost)

Modular and scalable architecture

Real-time web research
