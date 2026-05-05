import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai.resources.containers.files import content
from openai.types.shared_params import reasoning_effort
load_dotenv("deepseek_key.env")
app = FastAPI()

client=OpenAI(
    api_key=os.getenv("deepseek_key"),
    base_url="https://api.deepseek.com/v1"
)#{{"role": "system", "content": "你是一个资深二次元"}}
memory={
    "DONGHUA":[{"role": "system", "content": "你是一个资深二次元"}],
    "GAME":[{"role": "system", "content": "你是资深游戏玩家"}]
}
#请求体
class ChatRequest(BaseModel):
    user_id: str
    message: str
@app.post("/chat")
async def chat(req : ChatRequest ):
    user_id=req.user_id
    message=req.message
    if user_id not in memory:
        memory[user_id]=[
            {"role":"system","content":"请问您有什么需要？"}
        ]
    memory[user_id].append({"role":"user","content":message})
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=memory[user_id],
    stream=False,
    max_tokens=200,
    extra_body={"thinking": {"type": "enabled"}}
    )
    reply= response.choices[0].message.content
    memory[user_id].append({"role":"assistant","content":reply})
    return{"reply":reply}