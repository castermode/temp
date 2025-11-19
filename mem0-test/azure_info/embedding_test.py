"""
写代码，按照如下信息，向模型发送一个文本"你是谁"，并打印模型返回的embedding。


模型：text-embedding-3-small
"""

import requests
import json
import os

# Azure OpenAI Embedding API 配置
endpoint_url = "https://bk-cloud.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15"
api_key = os.getenv("TEXT_EMBEDDING_3_SMALL")

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# 设置请求体
data = {
    "input": "你是谁"
}

# 发送请求
try:
    response = requests.post(endpoint_url, headers=headers, json=data)
    response.raise_for_status()  # 如果请求失败则抛出异常
    
    # 解析响应
    result = response.json()
    
    # 打印模型返回的 embedding
    print("模型返回的 embedding：")
    embedding = result['data'][0]['embedding']
    print(f"维度: {len(embedding)}")
    print(f"前10个值: {embedding[:10]}")
    print(f"\n完整 embedding: {embedding}")
    
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"响应内容：{e.response.text}")
except KeyError as e:
    print(f"解析响应失败：{e}")
    print(f"完整响应：{json.dumps(result, indent=2, ensure_ascii=False)}")