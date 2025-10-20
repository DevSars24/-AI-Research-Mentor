from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import time
from dotenv import load_dotenv
from functools import lru_cache
from typing import List, Dict, Any
import random  # For sampling if memory is huge

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()

# -----------------------------
# Optional Gemini client
# -----------------------------
GEMINI_AVAILABLE = False
genai = None
genai_client = None
try:
    import google.generativeai as genai_lib
    genai = genai_lib
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"[DEBUG] Gemini library not available: {e}")
    GEMINI_AVAILABLE = False

# -----------------------------
# Local imports (safe fallbacks)
# -----------------------------
try:
    from reflection import reflect_answer
except Exception:
    def reflect_answer(answer, query, ctx):
        return f"[Reflection simulated for: {query}]"

try:
    from workflows import plan_and_execute
except Exception:
    def plan_and_execute(query):
        return f"[Plan simulated for: {query}]"

try:
    from tools import web_search_tool
except Exception:
    def web_search_tool(query):
        return f"[Web search simulated for: {query}]"

# -----------------------------
# Semantic embeddings
# -----------------------------
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"[DEBUG] sentence_transformers not available: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

@lru_cache()
def get_embed_model():
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise RuntimeError("sentence_transformers not installed")
    print("[DEBUG] Loading embedding model...")
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise RuntimeError("sentence_transformers not installed")
    if text is None:
        text = ""
    model = get_embed_model()
    return model.encode(text, convert_to_tensor=True)

# -----------------------------
# File paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")
GRAPH_FILE = os.path.join(BASE_DIR, "graph.json")
USER_PROFILE_FILE = os.path.join(BASE_DIR, "user_profile.json")
FINE_TUNE_FILE = os.path.join(BASE_DIR, "fine_tune_data.jsonl")

def ensure_file(path, blank):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(blank, f)

ensure_file(MEMORY_FILE, [])
ensure_file(GRAPH_FILE, {})
ensure_file(USER_PROFILE_FILE, {})

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"[DEBUG] {request.method} {request.url}")
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"[DEBUG] Response: {response.status_code} (took {duration:.2f}s)")
    return response

# -----------------------------
# Gemini init
# -----------------------------
if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        try:
            genai_client = genai.GenerativeModel(model_name)
        except Exception:
            genai_client = genai
        print("[DEBUG] Gemini client initialized.")
    except Exception as e:
        print(f"[DEBUG] Gemini init failed: {e}")
        genai_client = None

# -----------------------------
# JSON Helpers
# -----------------------------
def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [] if path == MEMORY_FILE else {}

def save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[DEBUG] Save JSON failed: {e}")

# -----------------------------
# Enhanced Semantic Memory Retrieval (RAG Core)
# -----------------------------
def retrieve_semantic_context(query: str, top_k=3, max_history=5):
    """
    RAG Implementation: Embed query, retrieve top-k similar past Q&A chunks,
    then build a chained context summary for generation.
    """
    try:
        mem = load_json(MEMORY_FILE)
        if not mem:
            return ""
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Fallback: Recent history only
            recent = mem[-top_k:]
            chunks = [f"Past: Q: {m.get('query','')}\nA: {m.get('answer','')[:200]}..." for m in recent]
            return "\n".join(chunks)
        
        query_vec = embed_text(query)
        scored_chunks = []
        
        # Sample recent memory to avoid OOM on large files (increased for better coverage)
        sample_mem = random.sample(mem[-500:], min(100, len(mem[-500:])))  # Sample up to 100 recent
        
        for m in sample_mem:
            # Embed the full Q&A as a "chunk" for better relevance (improved: average Q and A vecs)
            q_text = m.get("query", "")
            a_text = m.get("answer", "")[:200]  # Truncate long answers
            try:
                q_vec = embed_text(q_text)
                a_vec = embed_text(a_text)
                chunk_vec = (q_vec + a_vec) / 2  # Average for richer similarity
                sim = util.pytorch_cos_sim(query_vec, chunk_vec).item()
                if sim > 0.2:  # Threshold to filter low-relevance
                    chunk_text = f"Q: {q_text}\nA: {a_text}"
                    scored_chunks.append((sim, chunk_text))
                    print(f"[DEBUG] Sim score: {sim:.3f} for chunk: {q_text[:30]}...")  # Debug log
            except Exception as e:
                print(f"[DEBUG] Embedding chunk error: {e}")
        
        # Top-k similar chunks
        top_chunks = sorted(scored_chunks, key=lambda x: x[0], reverse=True)[:top_k]
        
        # Chain into a coherent context (e.g., "From past chats: [chunk1] [chunk2]")
        rag_context = "From past learning:\n" + "\n---\n".join([chunk for _, chunk in top_chunks])
        
        # Add recent history for multi-turn feel (last max_history entries)
        recent_history = mem[-max_history:]
        recent_str = "\nRecent chats:\n" + "\n".join([
            f"Q: {m.get('query','')[:50]}... A: {m.get('answer','')[:100]}..."
            for m in recent_history if m.get('query') != query  # Avoid self-reference
        ])
        
        full_rag = rag_context + "\n" + recent_str
        print(f"[DEBUG] RAG context length: {len(full_rag)} chars")  # Debug log
        return full_rag
        
    except Exception as e:
        print(f"[DEBUG] Enhanced RAG error: {e}")
        return "No past context available—starting fresh!"

# -----------------------------
# New: Build Full Conversation Context
# -----------------------------
def build_conversation_context(user_id: str, query: str, rag_context: str, profile: Dict[str, Any]):
    """
    Context Answering: Weave RAG + profile + style into a prompt-ready string.
    Makes responses feel learned/personalized without dumping raw data.
    """
    topics = ", ".join([k for k, v in sorted(profile.get("topics", {}).items(), key=lambda x: x[1], reverse=True)[:3]])
    style_prompt = f"Respond in a {profile.get('style', 'friendly')} tone, tying into user's interests: {topics}."
    
    # Improved: Summarize if too long
    if len(rag_context) > 1000:
        rag_context = rag_context[:1000] + "\n... (summarized for focus)"
    
    full_context = f"""
Conversation Context:
- User Interests: {topics}
- Learned from Past: {rag_context}  # Truncated for prompt limits
- Style Guide: {style_prompt}

Current Query: {query}
Use this to answer thoughtfully, building on what we've discussed before. ALWAYS reference 1-2 past points explicitly, e.g., 'Like we discussed in your lists query...'.
"""
    print(f"[DEBUG] Full context length: {len(full_context)} chars")  # Debug log
    return full_context

# -----------------------------
# New: Fine-Tuning Data Logger
# -----------------------------
def log_for_fine_tuning(user_id: str, query: str, context: str, answer: str):
    """
    Log Q&A in Alpaca format for fine-tuning (e.g., with Hugging Face TRL).
    """
    try:
        entry = {
            "instruction": "You are an AI mentor for students learning AI & programming. Explain step-by-step.",
            "input": context,
            "output": answer
        }
        with open(FINE_TUNE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[DEBUG] Logged for fine-tuning: {len(open(FINE_TUNE_FILE).readlines())} entries")
    except Exception as e:
        print(f"[DEBUG] Fine-tune logging error: {e}")

# -----------------------------
# Updated Graph (Optional, Simplified for Learning)
# -----------------------------
# Remove old graph usage. New: Use graph for topic clustering (not direct retrieval)
def update_learning_graph(query: str):
    """
    Simplified: Track topics for future RAG filtering, not direct word dumps.
    Improved: Better topic extraction (words >3 chars).
    """
    try:
        graph = load_json(GRAPH_FILE)
        if not isinstance(graph, dict):
            graph = {}
        
        # Extract key topics: longer words for better clustering
        key_topic = ' '.join([w for w in query.lower().split() if len(w) > 3])[:20].strip()
        if not key_topic:
            key_topic = "misc"
        graph.setdefault(key_topic, 0)
        graph[key_topic] += 1
        
        # Prune to top 50 topics
        top_topics = dict(sorted(graph.items(), key=lambda x: x[1], reverse=True)[:50])
        save_json(GRAPH_FILE, top_topics)
        print(f"[DEBUG] Graph updated for topic: {key_topic}")  # Debug log
    except Exception as e:
        print(f"[DEBUG] Graph update error: {e}")

# -----------------------------
# User Personalization
# -----------------------------
def update_user_profile(user_id, query):
    try:
        profile = load_json(USER_PROFILE_FILE)
        if user_id is None:
            user_id = "default_user"
        if user_id not in profile:
            profile[user_id] = {"topics": {}, "style": "friendly"}
        for word in query.split():
            profile[user_id]["topics"][word] = profile[user_id]["topics"].get(word, 0) + 1
        save_json(USER_PROFILE_FILE, profile)
    except Exception as e:
        print(f"[DEBUG] update_user_profile error: {e}")

def get_user_profile(user_id):
    try:
        profile = load_json(USER_PROFILE_FILE)
        return profile.get(user_id, {"style": "friendly", "topics": {}})
    except Exception:
        return {"style": "friendly", "topics": {}}

# -----------------------------
# Tool Handling
# -----------------------------
def choose_tool(query):
    q = (query or "").lower()
    if "search" in q or "latest" in q:
        return "web_search"
    elif "code" in q or "run" in q:
        return "code_runner"
    return "none"

def execute_tool(tool, query):
    try:
        if tool == "web_search":
            return web_search_tool(query)
        elif tool == "code_runner":
            return "[Code Runner] Simulated: code executed successfully."
    except Exception as e:
        print(f"[DEBUG] execute_tool error: {e}")
    return None

# -----------------------------
# System Prompt
# -----------------------------
SYSTEM_PROMPT = """
You are an AI mentor for students learning AI & programming.
Always explain step-by-step, clearly, and with runnable examples.
Use memory and adapt to user interests.
"""

# -----------------------------
# Local LLM simulation (Improved for better context use)
# -----------------------------
def local_llm_simulate(messages, context="", profile="friendly"):
    user_msg = ""
    for m in messages:
        if m.get("role") == "user":
            user_msg = m.get("content", "")
    return (
        f"[SIMULATED RESPONSE]\n"
        f"Style: {profile}\n\nBased on context: {context[:500]}...\n\n"
        f"Question: {user_msg}\n"
        "→ Step 1: Understand (tie to past if relevant)\n→ Step 2: Plan\n→ Step 3: Answer with example.\n"
    )

# -----------------------------
# LLM Wrapper
# -----------------------------
def generate_llm_response(prompt: str, user_query: str, style: str):
    if genai_client:
        try:
            if hasattr(genai_client, "generate_content"):
                resp = genai_client.generate_content(prompt)
                if hasattr(resp, "text"):
                    return resp.text
                return str(resp)
        except Exception as e:
            print(f"[DEBUG] Gemini failed: {e}")
    return local_llm_simulate([{"role": "user", "content": user_query}], prompt, style)

# -----------------------------
# Schemas
# -----------------------------
class ChatRequest(BaseModel):
    query: str
    user_id: str | None = "default_user"

# -----------------------------
# Health
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "OK", "message": "GenAI backend active."}

# -----------------------------
# MAIN CHAT
# -----------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        start_time = time.time()
        user_query = (req.query or "").strip()
        print(f"[DEBUG] New query: {user_query}")

        # Personalization
        update_user_profile(req.user_id, user_query)
        profile = get_user_profile(req.user_id)
        style = profile.get("style", "friendly")

        # Planning (keep as-is)
        try:
            plan = plan_and_execute(user_query)
        except Exception as e:
            print(f"[DEBUG] plan_and_execute error: {e}")
            plan = "[Plan unavailable]"

        # Enhanced RAG Context
        try:
            rag_context = retrieve_semantic_context(user_query, top_k=3, max_history=5)
        except Exception as e:
            print(f"[DEBUG] RAG error: {e}")
            rag_context = ""

        # Build Full Context
        full_context = build_conversation_context(req.user_id, user_query, rag_context, profile)

        # Tool (keep as-is)
        tool_name = choose_tool(user_query)
        try:
            tool_result = execute_tool(tool_name, user_query)
        except Exception as e:
            print(f"[DEBUG] Tool error: {e}")
            tool_result = None

        # Updated System Prompt with Context
        updated_system = f"""
{SYSTEM_PROMPT}

{full_context}

[Tool Output]: {tool_result if tool_result else 'None'}
"""

        # Generate Response
        try:
            answer = generate_llm_response(updated_system, user_query, style)
        except Exception as e:
            print(f"[DEBUG] LLM error: {e}")
            answer = local_llm_simulate([{"role": "user", "content": user_query}], full_context, style)

        # Reflection (keep as-is, but pass full_context)
        try:
            if callable(reflect_answer):
                reflection = reflect_answer(answer, user_query, full_context)
            else:
                reflection = "[Reflection simulated]"
        except Exception as e:
            print(f"[DEBUG] Reflection error: {e}")
            reflection = "[Reflection failed]"

        # Save Memory (keep as-is)
        try:
            mem = load_json(MEMORY_FILE)
            if not isinstance(mem, list):
                mem = []
            mem.append({
                "user_id": req.user_id,
                "query": user_query,
                "answer": answer,
                "plan": plan,
                "reflection": reflection,
                "ts": time.time()
            })
            if len(mem) > 1000:
                mem = mem[-1000:]
            save_json(MEMORY_FILE, mem)
        except Exception as e:
            print(f"[DEBUG] Memory save error: {e}")

        # Update Graph & Log for Fine-Tuning
        update_learning_graph(user_query)
        log_for_fine_tuning(req.user_id, user_query, full_context, answer)

        print(f"[DEBUG] Completed in {time.time()-start_time:.2f}s")
        return {
            "answer": answer,
            "reflection": reflection,
            "plan": plan,
            "meta": {
                "summary": (str(answer).split('\n')[0])[:200],
                "tool_used": tool_name,
                "rag_used": len(rag_context.split()) > 0,  # Flag if RAG kicked in
                "next_steps": ["Ask follow-up for deeper context", "Share code to run", "Explore related topics"],
            },
        }

    except Exception as e:
        print(f"[DEBUG] Outer error: {e}")
        return {"error": str(e)}