import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI

from openai.resources.containers.files import content
from openai.types.shared_params import reasoning_effort

load_dotenv("deepseek_key.env")
app = FastAPI()
client=OpenAI(
    api_key=os.getenv("deepseek_key"),
    base_url="https://api.deepseek.com/v1"
)
response =client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role":"system","content":"你是一个资深二次元"},
             {"role":"user","content":"你好"}
],
    stream=False,
    extra_body={"thinking": {"type": "enabled"}}
)
print(response.choices[0].message.content)