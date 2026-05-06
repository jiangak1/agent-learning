import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv("deepseek_key.env")

app = FastAPI()
client=OpenAI(
    api_key=os.getenv("deepseek_key"),
    base_url="https://api.deepseek.com/v1"
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_game_info",
            "description": "获取游戏的类型、Steam定价、开发商等信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "game_name": {
                        "type": "string",
                        "description": "游戏名称，例如 '黑神话：悟空'"
                    }
                },
                "required": ["game_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calculator",
            "description": "计算用户提供的数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2+3*4' 或 '10/2'"
                    }
                },
                "required": ["expression"]
              }
        }
    }
]
memory={
    "GAME":[{"role":"system","content":"你是一个游戏专家"}],
    "MATH":[{"role":"system","content":"你是一个数学老师"}]
}
class ChatRequest(BaseModel):
    user_id:str
    message:str
def get_game_info(game_name: str):
    try:
        url = "https://api.rawg.io/api/games"
        params = {
            "search": game_name,
            "page_size": 1,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            return "❌ 没找到这个游戏"
        game = data["results"][0]
        name = game.get("name", "未知")
        genres = [g["name"] for g in game.get("genres", [])]
        platforms = [
            p["platform"]["name"]
            for p in game.get("platforms", [])
        ]
        game_id = game["id"]
        detail_url = f"https://api.rawg.io/api/games/{game_id}"
        detail_resp = requests.get(detail_url, timeout=10)
        detail_resp.raise_for_status()
        detail = detail_resp.json()
        developers = [d["name"] for d in detail.get("developers", [])]
        return (
            f"🎮 游戏：{name}\n"
            f"📂 类型：{', '.join(genres) if genres else '未知'}\n"
            f"🏢 开发商：{', '.join(developers) if developers else '未知'}\n"
            f"🖥️ 平台：{', '.join(platforms) if platforms else '未知'}"
        )
    except Exception as e:
        return f"查询失败:{str(e)}"

def calculator(expression: str):
     try:
         allowed_chars = "0123456789+-*/(). "
         for char in expression:
            if char not in allowed_chars:
                return "非法表达式"

         result = eval(expression, {"__builtins__": None}, {})
         return str(result)
     except:
         return "计算错误"

tool_map={
    "get_game_info":get_game_info,
    "get_calculator":calculator
}

@app.post("/chat")
async def chat(req : ChatRequest ):
    user_id=req.user_id
    message=req.message
    if user_id not in memory:
        memory[user_id]=[
            {"role":"system","content":"请问您有什么需要？"}
        ]
    memory[user_id].append({"role":"user","content":message})
    # ---第一次访问
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=memory[user_id],
        tools=tools,
        stream=False,
        max_tokens=200,
        extra_body={"thinking": {"type": "enabled"}}
    )
    msg=response.choices[0].message
    if msg.tool_calls:
        tool_call=msg.tool_calls[0]
        function_name=tool_call.function.name
        args=json.loads(tool_call.function.arguments)
        try:
            result=tool_map[function_name](**args)
        except Exception as e:
            result=f"工具调用失败:{str(e)}"
        memory[user_id].append(msg)
        memory[user_id].append(
            {
            "role":"tool",
            "tool_call_id":tool_call.id,
            "content":str(result)
             })
        final_response=client.chat.completions.create(
           model="deepseek-v4-flash",
           messages=memory[user_id],
        )
        reply=final_response.choices[0].message.content
        memory[user_id].append({"role":"assistant","content":reply})
        return{"reply":reply}
    reply=msg.content
    memory[user_id].append({"role":"assistant","content":reply})
    return{"reply":reply}