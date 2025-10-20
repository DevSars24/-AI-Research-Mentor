# 🤖 AI Research Mentor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![React 18+](https://img.shields.io/badge/React-18%2B-lightblue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal)](https://fastapi.tiangolo.com/)
[![Vite](https://img.shields.io/badge/Vite-4%2B-orange)](https://vitejs.dev/)

---

## 🎯 Project Overview

**AI Research Mentor** is a full-stack AI-powered chatbot designed as a personal mentor for students and developers exploring **Artificial Intelligence (AI)**, **Machine Learning (ML)**, and **programming concepts**. Built with cutting-edge technologies like **Retrieval-Augmented Generation (RAG)**, **Gemini API**, and semantic embeddings, it provides contextual, step-by-step guidance tailored to your learning journey.

### Why This Project?
- **Personalized Learning**: Tracks your interests (e.g., RAG, embeddings) and builds on past conversations without "forgetting."
- **Interactive & Engaging**: Explains concepts with code examples, analogies, and tools like web search simulation.
- **Production-Ready**: Lightweight backend with fallbacks, fine-tuning prep, and a sleek React frontend.
- **Educational Focus**: Ideal for 2nd-year B.Tech students diving into LLMs, LangChain, and beyond—turning code into real impact!

This project was crafted in October 2025 as a showcase of modern AI tooling, blending backend robustness with frontend polish.

---

## ✨ Key Features

- **RAG-Powered Memory**: Retrieves and chains past queries semantically (using SentenceTransformers) for continuous conversations.
- **Personalization**: User profiles track topics and styles (e.g., "friendly" tone) via JSON.
- **Tool Integration**: Simulated web search, code execution, and planning workflows.
- **Fine-Tuning Ready**: Logs interactions in Alpaca format for easy model customization (e.g., via Hugging Face).
- **Bilingual Support**: Handles Hindi-English queries seamlessly.
- **Responsive UI**: Dark-themed chat interface with animations, loading states, and health checks.
- **Secure & Scalable**: `.env`-based secrets, CORS middleware, and modular structure.

---

## 🛠️ Tech Stack

| Category       | Technologies/Tools                          |
|----------------|---------------------------------------------|
| **Backend**    | FastAPI, Python 3.10+, Google Gemini, SentenceTransformers, Pydantic |
| **Frontend**   | React 18+, Vite, Tailwind-inspired CSS (vanilla) |
| **Database**   | JSON files (memory.json, graph.json for lightweight persistence) |
| **AI/ML**      | RAG, Embeddings (all-MiniLM-L6-v2), Fine-Tuning (Alpaca format) |
| **Dev Tools**  | dotenv, uvicorn, ESLint, Prettier          |
| **Deployment** | Ready for Vercel (frontend), Render/Heroku (backend) |

---

## 📋 Project Structure

Here's a breakdown of the monorepo structure for easy navigation:

```
ai-research-mentor/
├── backend/                  # FastAPI server with AI logic
│   ├── app.py                # Main app: Endpoints (/chat, /health), RAG, tools
│   ├── .env                  # Secrets (API keys)—ignored by Git!
│   ├── fine_tune_data.jsonl  # Logged Q&A for fine-tuning models
│   ├── graph.json            # Topic clustering for RAG enhancement
│   ├── memory.json           # Conversation history (semantic retrieval)
│   ├── reflection.py         # Answer reflection (clarity/relevance checks)
│   ├── requirements.txt      # Python deps (FastAPI, sentence-transformers, etc.)
│   ├── tools.py              # Web search & code runner tools
│   ├── user_profile.json     # Per-user topics/styles
│   └── workflows.py          # Query planning steps
├── frontend/                 # React client for chat UI
│   ├── public/               # Static assets (index.html, favicon)
│   ├── src/
│   │   └── components/
│   │       └── ChatBox.jsx   # Main chat component with animations & API calls
│   ├── .gitignore            # Frontend-specific ignores (node_modules)
│   ├── eslintrc.js           # ESLint config for code quality
│   ├── index.html            # Entry HTML
│   ├── package.json          # NPM deps (React, etc.)
│   ├── package-lock.json     # Locked deps
│   ├── README.md             # Frontend-specific notes (optional)
│   └── vite.config.js        # Vite bundler config
├── .gitignore                # Root-level: Ignores .env, node_modules, etc.
└── README.md                 # This file!
```

- **Backend Focus**: Modular with fallbacks (e.g., simulated tools if libs missing).
- **Frontend Focus**: Single-file ChatBox for simplicity—expands easily.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18+): For frontend.
- **Python** (3.10+): For backend.
- **API Key**: Get a free [Google Gemini API key](https://makersuite.google.com/app/apikey) and add to `.env`.

### 1. Clone & Setup
```bash
git clone <your-repo-url> ai-research-mentor
cd ai-research-mentor
```

### 2. Backend Setup
```bash
cd backend
# Install deps
pip install -r requirements.txt

# Add secrets to .env (create if missing)
echo "GEMINI_API_KEY=your_key_here" > .env

# Run server
uvicorn app:app --reload --port 8000
```
- Test: Visit `http://localhost:8000/health` → Should return `{"status": "OK"}`.

### 3. Frontend Setup
```bash
cd ../frontend
# Install deps
npm install

# Run dev server
npm run dev
```
- Opens at `http://localhost:5173` (Vite default). Chat connects to backend at `/chat`.

### 4. Full Run
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Chat away! Try: "Explain RAG in AI with code."

---

## 📖 Usage Guide

### Backend Endpoints
| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/health` | GET | Server status check. | `curl http://localhost:8000/health` |
| `/chat` | POST | Send query for AI response. | `{"query": "What is RAG?"}` → Returns answer + meta (RAG used, tools). |

- **Request Body** (JSON): `{ "query": "string", "user_id": "optional_string" }`
- **Response**: `{ "answer": "string", "reflection": "string", "plan": "string", "meta": { ... } }`

### Frontend Features
- **Chat Interface**: Dark gradient theme, auto-scroll, Enter-to-send.
- **Loading States**: Animated dots/spinner during API calls.
- **Health Button**: Quick backend ping with alert.
- **Responsive**: Mobile-friendly (stacked header on small screens).

### Example Conversation
1. User: "Python lists samjhao."
   - AI: Step-by-step explanation + code snippet.
2. User: "Ab lists ko RAG mein use karo."
   - AI: References past + RAG example.

Data persists in JSON files—clear `memory.json` to reset.

---

## 🔧 Customization & Extensions

- **Add Real Tools**: Update `tools.py` with SerpAPI for live web search.
- **Fine-Tune Model**: Run `fine_tune.py` (from earlier scripts) on `fine_tune_data.jsonl`.
- **Deploy**:
  - **Backend**: Render.com (free tier) → Env vars for keys.
  - **Frontend**: Vercel/Netlify → Proxy `/chat` to backend URL.
- **Themes**: Tweak CSS in `ChatBox.jsx` for light mode.

### Potential Enhancements
- Voice input (Web Speech API).
- Multi-user support (SQLite instead of JSON).
- Analytics: Track query trends via graph.json.

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/amazing-idea`.
3. Commit changes: `git commit -m "Add: RAG visualization"`.
4. Push: `git push origin feature/amazing-idea`.
5. Open a Pull Request!

Feedback? Issues? Open one—let's build together!

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Inspired by xAI's Grok for helpful, truthful AI.
- Thanks to Google for Gemini API.
- Built with love for aspiring AI devs—may your code turn into impact! 🚀

**Stars & Forks Welcome!** ⭐ If this helps, give it a star on GitHub.

