import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

load_dotenv()

app = FastAPI(title="AI Smart Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

_graph = None
_graph_lock = asyncio.Lock()

async def get_graph():
    global _graph
    if _graph is None:
        async with _graph_lock:
            if _graph is None:
                from agent import graph
                _graph = graph
    return _graph

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"

@app.get("/health")
async def health():
    return {"status": "ok", "message": "AI Smart Chatbot API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document (PDF, TXT, DOCX, etc.) for RAG context."""
    allowed_extensions = {".pdf", ".txt", ".docx", ".csv", ".json", ".md"}
    ext = Path(file.filename).suffix.lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    dest = DATA_DIR / file.filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    global _graph
    _graph = None

    return {
        "message": f"File '{file.filename}' uploaded successfully.",
        "filename": file.filename,
        "size": dest.stat().st_size,
    }

@app.get("/files")
async def list_files():
    """List uploaded files."""
    files = []
    for f in DATA_DIR.iterdir():
        if f.is_file():
            files.append({"name": f.name, "size": f.stat().st_size})
    return {"files": files}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete an uploaded file."""
    target = DATA_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    target.unlink()
    global _graph
    _graph = None
    return {"message": f"File '{filename}' deleted."}

@app.post("/chat")
async def chat(req: ChatRequest):
    """Non-streaming chat endpoint."""
    graph = await get_graph()
    config = {"configurable": {"thread_id": req.thread_id}}
    from langchain_core.messages import HumanMessage
    result = await asyncio.to_thread(
        graph.invoke,
        {"messages": [HumanMessage(content=req.message)]},
        config
    )
    last_msg = result["messages"][-1]
    return {"response": last_msg.content, "thread_id": req.thread_id}

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat endpoint — yields tokens word by word via SSE."""
    from langchain_core.messages import HumanMessage

    async def event_generator():
        graph = await get_graph()
        config = {"configurable": {"thread_id": req.thread_id}}

        result = await asyncio.to_thread(
            graph.invoke,
            {"messages": [HumanMessage(content=req.message)]},
            config
        )
        last_msg = result["messages"][-1]
        content = last_msg.content

        words = content.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.03)

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
