from tools import tools, tool_map
from memory import memory
from config import client
import json
from logger import logger
def run_agent(user_id,message):
    if user_id not in memory:
        memory[user_id] = [
            {"role": "system", "content": "请问您有什么需要？"}
        ]
    logger.info(f"用户消息:{message}")
    memory[user_id].append({"role": "user", "content": message})
    # 初始访问---------------------------------------------------------

    max_steps = 3
    for _ in range(max_steps):
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=memory[user_id],
            tools=tools,
            max_tokens=200,
            extra_body={"thinking": {"type": "enabled"}}
        )
        msg = response.choices[0].message

        # 没有tool_calls说明结束了
        if not msg.tool_calls:
            reply = msg.content
            memory[user_id].append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )
            if len(memory[user_id]) > 20:
                memory[user_id] =(
                    memory[user_id][:1]+
                    memory[user_id][-19:]
                )
            return {"reply": reply}
        memory[user_id].append(msg)
        for tool_call in msg.tool_calls:
            function_name = tool_call.function.name
            logger.info(f"调用工具:{function_name}")
            args = json.loads(tool_call.function.arguments)
            try:
                result = tool_map[function_name](**args)
                logger.info(f"工具结果:{result}")
            except Exception as e:
                result = logger.info(f"工具错误:{str(e)}")
            memory[user_id].append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)}
            )
            continue