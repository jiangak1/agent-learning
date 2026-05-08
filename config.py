import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("deepseek_key.env")

client = OpenAI(
    api_key=os.getenv("deepseek_key"),
    base_url="https://api.deepseek.com/v1"
)