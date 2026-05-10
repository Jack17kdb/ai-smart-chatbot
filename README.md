<div align="center">
  <h1>🤖 AI Smart Chatbot</h1>
  <p><strong>A production-grade RAG-powered AI chatbot built with FastAPI · LangGraph · Groq · React · Tailwind CSS</strong></p>
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-green" />
  <img alt="React" src="https://img.shields.io/badge/React-19-61dafb" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688" />
</div>

---

## ✨ Overview

AI Smart Chatbot is a full-stack, production-ready intelligent assistant that lets you upload your own documents (PDFs, DOCX, TXT, CSV) and chat with them using the power of **LLaMA 3.3 70B** via Groq. Built on a RAG (Retrieval-Augmented Generation) pipeline with LangGraph, it remembers conversation context, streams responses word by word, and surfaces answers from your own knowledge base.

### Key Features

- 🔍 **RAG Pipeline** — ChromaDB vector search + HuggingFace embeddings
- ⚡ **Streaming** — real-time word-by-word AI response streaming via SSE
- 📁 **File Upload** — drag-and-drop sidebar for PDF, DOCX, TXT, CSV
- 🧠 **Memory** — LangGraph conversation checkpointing per session
- 🎨 **Modern Dark UI** — Tailwind CSS v4, animated typing indicator, smooth UX
- 🚀 **Production-ready** — deploy free on Render in minutes

---

## 🗂 Project Structure

```
ai-smart-chatbot/
├── ai-service/              # FastAPI + LangGraph backend
│   ├── main.py              # API routes (chat, upload, files)
│   ├── agent.py             # LangGraph RAG agent
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (never commit)
│   ├── .env.example         # Safe template to commit
│   └── data/                # Uploaded documents (gitignored)
├── frontend/                # React + Tailwind v4 frontend
│   ├── src/
│   │   ├── App.jsx          # Main chat UI (sidebar, streaming, etc.)
│   │   ├── index.css        # Tailwind + custom animations
│   │   └── main.jsx         # React entry point
│   ├── vite.config.js
│   └── package.json
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start — Run Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-smart-chatbot.git
cd ai-smart-chatbot
```

### 2. Backend setup

```bash
cd ai-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the API server
uvicorn main:app --reload --port 8000
```

API is now live at **http://localhost:8000**  
Swagger docs at **http://localhost:8000/docs**

### 3. Frontend setup

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Frontend is now live at **http://localhost:5173**

---

## 🌐 Deploy on Render (Free)

### Backend (Web Service)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo, select the `ai-service/` directory
4. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variable:** `GROQ_API_KEY = your_key_here`
6. Click **Deploy**

### Frontend (Static Site)

1. Go to [render.com](https://render.com) → **New Static Site**
2. Connect the same repo, select the `frontend/` directory
3. Settings:
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Add **Environment Variable:** `VITE_API_URL = https://your-backend.onrender.com`
5. Update `vite.config.js` proxy target to your Render backend URL
6. Click **Deploy**

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload` | Upload a document |
| GET | `/files` | List uploaded files |
| DELETE | `/files/{name}` | Delete a file |
| POST | `/chat` | Non-streaming chat |
| POST | `/chat/stream` | Streaming chat (SSE) |

### Chat request body

```json
{
  "message": "Summarize this document",
  "thread_id": "session-abc123"
}
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | LLaMA 3.3 70B via Groq |
| Agent | LangGraph + LangChain |
| Vector DB | ChromaDB |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + Tailwind CSS v4 |
| State | Zustand |
| Animations | GSAP + CSS |
| Streaming | Server-Sent Events (SSE) |

---

## 📄 License

MIT — free to use, modify, and deploy.

---

<div align="center">
  Built with ❤️ using open-source tools and the Groq API
</div>
