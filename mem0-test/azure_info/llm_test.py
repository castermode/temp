"""
写代码，按照如下信息，向模型发送一条消息"你是谁"，并打印模型返回的回答。

模型：gpt-4.1-nano-2025-04-14 
"""

import requests
import json
import os

# Azure OpenAI API 配置
endpoint_url = "https://bk-us-2.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2025-01-01-preview"
api_key = os.getenv("GPT_41_NANO_KEY")

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# 设置请求体
data = {
    "messages": [
        {
            "role": "user",
            "content": "你是什么版本的模型？"
        }
    ],  
    "max_tokens": 800,
    "temperature": 0.7
}

# 发送请求
try:
    response = requests.post(endpoint_url, headers=headers, json=data)
    response.raise_for_status()  # 如果请求失败则抛出异常
    
    # 解析响应
    result = response.json()
    
    # 打印模型返回的回答
    print("模型回答：")
    print(result['choices'][0]['message']['content'])
    
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")
except KeyError as e:
    print(f"解析响应失败：{e}")
    print(f"完整响应：{json.dumps(result, indent=2, ensure_ascii=False)}")