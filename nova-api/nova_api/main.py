from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio

# Import Core
from nova_core.engine.agent import Agent
from nova_core.models.ollama import OllamaClient
from nova_core.memory.memory import MemorySystem
from nova_core.config import config

# Import Tools
from nova_tools.standard.file import FileReadTool, FileWriteTool
from nova_tools.standard.shell import ShellRunTool
from nova_tools.standard.web import WebGetTool

app = FastAPI(title="Nova v2 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
tools = [
    FileReadTool(),
    FileWriteTool(),
    ShellRunTool(),
    WebGetTool()
]
agent = Agent(tools=tools)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/chat")
async def chat(request: ChatRequest):
    """Simple REST chat endpoint."""
    response_gen = agent.chat(request.message, request.session_id)
    full_response = ""
    for chunk in response_gen:
        full_response += chunk
    return {"response": full_response}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming chat."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            message = request.get("message")
            session_id = request.get("session_id")
            
            if not message:
                continue
                
            # Stream response
            for chunk in agent.chat(message, session_id):
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk
                }))
                # Small delay to allow UI to render
                await asyncio.sleep(0.01)
                
            await websocket.send_text(json.dumps({
                "type": "done"
            }))
            
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/models")
def get_models():
    return {"models": agent.client.get_models()}

@app.get("/tools")
def get_tools():
    return {"tools": [t.to_schema() for t in agent.tools.values()]}
