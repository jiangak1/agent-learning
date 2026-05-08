import requests
import json
import os


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
            "name": "calculator",
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

tool_map = {
    "get_game_info": get_game_info,
    "calculator": calculator
}