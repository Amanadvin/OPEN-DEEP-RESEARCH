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

## 5. High-Level Architecture

The architecture of Open Deep Research follows a layered multi-agent design.

![Open Deep Research Architecture](https://github.com/Amanadvin/OPEN-DEEP-RESEARCH/blob/main/Architecture_%20diagram.png)

### Architecture Description

- User Interface (UI): Users enter questions or research topics.

- Planner Agent: Breaks the main topic into smaller sub-questions and creates a research plan.

- Searcher Agent: Fetches relevant and reliable information from the web using Tavily API.

- Writer Agent: Analyzes and summarizes the collected data into a structured report using a local or hosted LLM (LM Studio / Ollama).

- Memory System: Stores previous questions and answers to maintain context for follow-up queries.

- Execution Graph (LangGraph): Connects all agents and manages the workflow from input to final output.

- Final Output: Delivers a clear and organized research report to the user.

---


## 6. Workflow
### 1. User Input

- User provides a research topic or question

### 2. Planning Phase

- Planner Agent breaks the topic into sub-questions

- Creates a structured research roadmap

### 3. Information Retrieval

- Searcher Agent queries the web using Tavily API

- Retrieves up-to-date and relevant sources

### 4. Synthesis

- Writer Agent analyzes retrieved content

- Generates coherent summaries using LLM

### 5. Report Generation

- All findings are compiled into a structured report

- Session Memory (Optional)

- Research threads stored for continuity

---

## 7. Agent Roles

### 1. Planner Agent

- Breaks down the main query

- Decides research strategy

- Creates sub-questions and flow

### 2. Searcher Agent

- Uses Tavily API

- Fetches relevant, real-time web data

- Filters noise from search results

 ### 3. Writer Agent

- Synthesizes retrieved content

- Generates structured summaries

- Produces final research report

### 4. Pipeline / Agent Flow

Managed using LangGraph

Controls execution order and dependencies

---
## 8. Outputs / Results

### Chat Output – Example 1

The following screenshot shows a sample research-based response generated by the system.

![Chat Output 1](https://github.com/LakshanLikhitM/OPEN-DEEP-RESEARCH/blob/main/output_chat1.png)
### Chat Output – Example 2

The following screenshot shows a follow-up question handled using session memory and conversational continuity.

![Chat Output 2](https://github.com/LakshanLikhitM/OPEN-DEEP-RESEARCH/blob/main/output_chat2.png)

---
## 9. Session Memory and Continuity Support

- The system remembers user messages during a session.

- Previous interactions are temporarily stored for reference.

- Follow-up questions are answered using the earlier conversation context.

- Users can continue the conversation naturally without repeating information.

- This helps provide a smooth, context-aware, and seamless user experience.

- This ensures a smooth and context-aware conversational experience.

---

## 10. Limitations

- Depends on external APIs (Tavily availability)

- Quality varies based on:

      - LLM used

      - Prompt clarity

- Local LLMs may be slower without GPU

- Not ideal for:

      - Highly confidential data

      - Real-time decision systems
---
## 10. Future Enhancements
Enhancements

- 🔗 Add citation formatting (APA / IEEE)

- 🌍 Multi-language research support

- 📈 Better memory retrieval & long-term context

- ☁ Cloud deployment (AWS / Azure / GCP)

- 🔐 User authentication & saved projects

- 🧠 Advanced reasoning agents

---

## 11. Deployed Project Link

🔗 Live Demo:

        - (Local URL: http://localhost:8501)
        - (Network URL: http://172.16.4.14:8501)

Example:
