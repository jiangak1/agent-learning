from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('deepseek_api_key'),
    base_url="https://api.deepseek.com/v1")

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}})

print(response.choices[0].message.content)
#post请求   r = requests.post('https://httpbin.org/post', data={'key': 'value'})
#更复杂的post可以另外设置data{}|dict
#r.json（）数据抓取
#import requests
# r = requests.post('https://httpbin.org/post', data={'key': 'value'})
#r.json()
#头部headers={ }|相当于一个dict