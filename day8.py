import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv("deepseek_key.env")

app = FastAPI()
client = OpenAI(
    api_key=os.getenv("deepseek_key"),
    base_url="https://api.deepseek.com/v1"
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_game_info",
            "description": "获取游戏的类型、Steam定价、开发商、价格等信息",
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
memory = {
    "GAME": [{"role": "system", "content": "你是一个游戏专家"}],
    "MATH": [{"role": "system", "content": "你是一个数学老师"}]
}


class ChatRequest(BaseModel):
    user_id: str
    message: str


def get_game_info(game_name: str):

    try:

        print("开始查询 RAWG")

        url = "https://api.rawg.io/api/games"

        params = {
            "key":os.getenv("rawg_key"),
            "search": game_name,
            "page_size": 1
        }

        resp = requests.get(
            url,
            params=params,
            timeout=10
        )

        print("RAWG状态码:", resp.status_code)
        print("RAWG返回:", resp.text)

        resp.raise_for_status()

        data = resp.json()

        if not data.get("results"):
            return "RAWG 没找到游戏"

        game = data["results"][0]

        name = game.get("name", "未知")

        genres = [
            g["name"]
            for g in game.get("genres", [])
        ]

        platforms = [
            p["platform"]["name"]
            for p in game.get("platforms", [])
        ]

        # -------------------------
        # CheapShark
        # -------------------------

        print("开始查询 CheapShark")

        cheap_url = "https://www.cheapshark.com/api/1.0/games"

        cheap_params = {
            "title": name
        }

        cheap_resp = requests.get(
            cheap_url,
            params=cheap_params,
            timeout=10
        )

        print("CheapShark状态码:", cheap_resp.status_code)
        print("CheapShark返回:", cheap_resp.text)

        price = "暂无价格"

        if cheap_resp.status_code == 200:

            cheap_data = cheap_resp.json()

            if cheap_data:

                price = cheap_data[0].get(
                    "cheapest",
                    "暂无价格"
                )

        return (
            f"🎮 游戏：{name}\n"
            f"📂 类型：{', '.join(genres)}\n"
            f"💰 最低价格：{price}\n"
            f"🖥️ 平台：{', '.join(platforms)}"
        )

    except Exception as e:

        print("发生错误:", str(e))

        return f"查询失败: {str(e)}"

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
#————————————————————————————————————————————————————————————————————————————

tool_map = {
    "get_game_info": get_game_info,
    "get_calculator": calculator
}
#——————————————————————————————————————————————————

@app.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    message = req.message
    if user_id not in memory:
        memory[user_id] = [
            {"role": "system", "content": "请问您有什么需要？"}
        ]
    memory[user_id].append({"role": "user", "content": message})
#初始访问---------------------------------------------------------

    max_steps = 3
    for _ in range(max_steps):
        response=client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=memory[user_id],
            tools=tools,
            max_tokens=200,
            extra_body={"thinking": {"type": "enabled"}}
        )
        msg=response.choices[0].message

#没有tool_calls说明结束了
        if not msg.tool_calls:
            reply =msg.content
            memory[user_id].append(
                {
                    "role":"assistant",
                    "content": reply
                }
            )
            return {"reply":reply}
        memory[user_id].append(msg)
        for tool_call in msg.tool_calls:
            function_name=tool_call.function.name
            args=json.loads(tool_call.function.arguments)
            try:
                result=tool_map[function_name](**args)
            except Exception as e:
                result=f"工具错误:{str(e)}"
            memory[user_id].append({
                 "role":"tool",
                "tool_call_id":tool_call.id,
                "content":str(result)}
            )
            continue









