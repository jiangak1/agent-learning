from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent
app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
@app.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    message = req.message
    reply=run_agent(
        req.user_id,
        req.message
    )
    return {"reply":reply}
