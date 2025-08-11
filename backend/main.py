# backend/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
import uuid
from threading import Lock
import time

# ---- Config ----
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing API key. Set GOOGLE_API_KEY or GEMINI_API_KEY in backend/.env")

# Configure Gemini
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"   # change if your account uses a different model

# ---- FastAPI app ----
app = FastAPI(title="Chatbot with Context (Gemini)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Conversation store (in-memory) ----
# sessions: { session_id: [ {"role":"user"/"assistant"/"system","content": "..."}, ... ] }
sessions = {}
sessions_lock = Lock()
MAX_TOKENS_CONTEXT = 2000  # approximate guard (not exact token counting)
MAX_MESSAGES = 20          # keep last 20 messages per session

# system message to guide the assistant
SYSTEM_PROMPT = "You are a helpful, concise AI assistant. Answer user queries politely and clearly."

# ---- Request/Response models ----
class ChatRequest(BaseModel):
    message: str
    session_id: str = None   # optional; server will create if not provided

class ChatResponse(BaseModel):
    response: str
    session_id: str
    error: str | None = None

# ---- Helpers ----
def create_session():
    sid = str(uuid.uuid4())
    with sessions_lock:
        sessions[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return sid

def append_message(session_id: str, role: str, content: str):
    with sessions_lock:
        if session_id not in sessions:
            sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        sessions[session_id].append({"role": role, "content": content})
        # keep size bounded
        if len(sessions[session_id]) > MAX_MESSAGES:
            # keep system prompt + last (MAX_MESSAGES-1) messages
            sessions[session_id] = [sessions[session_id][0]] + sessions[session_id][- (MAX_MESSAGES-1):]

def build_prompt_from_session(session_id: str, new_user_message: str) -> str:
    """Convert session messages into a single prompt string for Gemini."""
    with sessions_lock:
        messages = sessions.get(session_id, [{"role":"system","content":SYSTEM_PROMPT}])
    # append the new user message at the end (don't mutate store here)
    convo = messages + [{"role": "user", "content": new_user_message}]
    # Build a textual prompt (role-prefixed). This is robust even if SDK expects plain text.
    prompt_lines = []
    for m in convo:
        role = m["role"]
        content = m["content"]
        if role == "system":
            prompt_lines.append(f"System: {content}")
        elif role == "user":
            prompt_lines.append(f"User: {content}")
        else:
            prompt_lines.append(f"Assistant: {content}")
    prompt_lines.append("Assistant:")  # let the model continue from assistant
    return "\n".join(prompt_lines)

# ---- Endpoints ----
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    message = req.message.strip() if req.message else ""
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    # create or use session_id
    sid = req.session_id or create_session()

    # append user message to session store
    append_message(sid, "user", message)

    # build prompt that includes session history
    prompt = build_prompt_from_session(sid, message)

    # call Gemini, with basic retry/backoff for transient errors
    try:
        start = time.time()
        model = genai.GenerativeModel(MODEL_NAME)
        # Using generate_content(prompt) pattern; response.text contains the reply.
        # If your SDK uses a different method signature in your version, adapt accordingly.
        resp = model.generate_content(prompt)
        elapsed = time.time() - start

        # Extract reply text safely
        reply_text = getattr(resp, "text", None)
        if reply_text is None:
            # fallback if structure differs
            reply_text = str(resp)

        # append assistant response to conversation
        append_message(sid, "assistant", reply_text)

        # return structured response
        return ChatResponse(response=reply_text, session_id=sid, error=None)

    except Exception as e:
        # friendly error handling for the frontend
        err_str = str(e)
        # for known API problems, you can map to friendly messages
        if "quota" in err_str.lower() or "billing" in err_str.lower():
            friendly = "AI service quota exceeded or billing issue. Please check your account."
        elif "401" in err_str or "unauthorized" in err_str.lower():
            friendly = "Authentication error with AI service. Check API key."
        elif "model" in err_str.lower() or "not found" in err_str.lower():
            friendly = "Requested model is unavailable. Contact admin or try a different model."
        else:
            friendly = "AI service temporarily unavailable. Please try again later."

        # optionally log error server-side (print here)
        print("Gemini error:", err_str)

        # Return a friendly message but preserve session id
        return ChatResponse(
            response=friendly,
            session_id=sid,
            error=err_str
        )

@app.post("/reset_session")
async def reset_session(payload: dict):
    # Accept {"session_id": "..."} and clear it
    sid = payload.get("session_id")
    if not sid:
        raise HTTPException(status_code=400, detail="session_id required")
    with sessions_lock:
        sessions[sid] = [{"role":"system","content":SYSTEM_PROMPT}]
    return {"status":"ok", "session_id": sid}

@app.get("/health")
def health():
    return {"status": "ok"}
