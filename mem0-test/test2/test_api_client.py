"""
Mem0 API 客户端测试脚本
用于测试 mem0_server.py 提供的 REST API

运行前请确保：
1. 已启动 mem0_server.py
2. 已设置环境变量 GPT_41_NANO_KEY 和 TEXT_EMBEDDING_3_SMALL
"""

import requests
import json
from typing import List, Dict, Any


class Mem0Client:
    """Mem0 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def add_memory(
        self,
        messages: List[Dict[str, str]],
        user_id: str = "default_user",
        infer: bool = False
    ) -> Dict[str, Any]:
        """添加记忆"""
        data = {
            "messages": messages,
            "user_id": user_id,
            "infer": infer
        }
        response = requests.post(f"{self.base_url}/memories", json=data)
        return response.json()
    
    def search_memories(
        self,
        query: str,
        user_id: str = "default_user",
        limit: int = 5
    ) -> Dict[str, Any]:
        """搜索记忆"""
        data = {
            "query": query,
            "user_id": user_id,
            "limit": limit
        }
        response = requests.post(f"{self.base_url}/memories/search", json=data)
        return response.json()
    
    def get_all_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        """获取所有记忆"""
        response = requests.get(f"{self.base_url}/memories", params={"user_id": user_id})
        return response.json()
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """获取指定记忆"""
        response = requests.get(f"{self.base_url}/memories/{memory_id}")
        return response.json()
    
    def update_memory(self, memory_id: str, data: str) -> Dict[str, Any]:
        """更新记忆"""
        payload = {"data": data}
        response = requests.put(f"{self.base_url}/memories/{memory_id}", json=payload)
        return response.json()
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """删除记忆"""
        response = requests.delete(f"{self.base_url}/memories/{memory_id}")
        return response.json()
    
    def delete_all_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        """删除所有记忆"""
        response = requests.delete(f"{self.base_url}/memories", params={"user_id": user_id})
        return response.json()
    
    def get_history(self, user_id: str = "default_user") -> Dict[str, Any]:
        """获取历史记录"""
        response = requests.get(f"{self.base_url}/history", params={"user_id": user_id})
        return response.json()


def print_result(title: str, result: Dict[str, Any]):
    """美化打印结果"""
    print("\n" + "=" * 60)
    print(f"📌 {title}")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)


def main():
    """主测试流程"""
    # 创建客户端
    client = Mem0Client()
    user_id = "test_user_001"
    
    print("🚀 开始测试 Mem0 API")
    
    # 1. 健康检查
    print("\n[1/7] 健康检查...")
    result = client.health_check()
    print_result("健康检查结果", result)
    
    # 2. 添加记忆
    print("\n[2/7] 添加记忆...")
    messages = [
        {"role": "user", "content": "我喜欢吃苹果，因为它很甜。"},
        {"role": "assistant", "content": "知道了，您喜欢吃苹果。"}
    ]
    result = client.add_memory(messages=messages, user_id=user_id, infer=False)
    print_result("添加记忆结果", result)
    
    # 3. 再添加一条记忆
    print("\n[3/7] 添加第二条记忆...")
    messages = [
        {"role": "user", "content": "我最近在学习 Python 编程。"},
        {"role": "assistant", "content": "很好，Python 是一门很实用的语言。"}
    ]
    result = client.add_memory(messages=messages, user_id=user_id, infer=False)
    print_result("添加第二条记忆结果", result)
    
    # 4. 获取所有记忆
    print("\n[4/7] 获取所有记忆...")
    result = client.get_all_memories(user_id=user_id)
    print_result("所有记忆", result)
    
    # 5. 搜索记忆
    print("\n[5/7] 搜索记忆...")
    result = client.search_memories(query="我喜欢吃什么", user_id=user_id, limit=5)
    print_result("搜索结果", result)
    
    # 6. 获取历史记录
    print("\n[6/7] 获取历史记录...")
    result = client.get_history(user_id=user_id)
    print_result("历史记录", result)
    
    '''
    # 7. 测试更新和删除（可选）
    print("\n[7/7] 测试更新和删除...")
    all_memories = client.get_all_memories(user_id=user_id)
    if all_memories.get("data") and all_memories["data"].get("results"):
        # 获取第一条记忆的 ID
        first_memory = all_memories["data"]["results"][0]
        memory_id = first_memory.get("id")
        
        if memory_id:
            # 测试更新
            print(f"\n  更新记忆 {memory_id}...")
            update_result = client.update_memory(memory_id, "我喜欢吃苹果和香蕉")
            print(f"  更新结果: {update_result.get('success')}")
            
            # 测试删除单条
            print(f"\n  删除记忆 {memory_id}...")
            delete_result = client.delete_memory(memory_id)
            print(f"  删除结果: {delete_result.get('success')}")
    '''
    
    # 显示最终状态
    print("\n[最终状态] 当前所有记忆...")
    result = client.get_all_memories(user_id=user_id)
    print_result("最终记忆列表", result)
    
    print("\n✅ 所有测试完成！")
    print("\n💡 提示：")
    print("   - 访问 http://localhost:8000/docs 查看交互式 API 文档")
    print("   - 使用不同的 user_id 可以隔离不同用户的记忆")
    print("   - 设置 infer=True 可以启用 AI 推理功能")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器！")
        print("请确保 mem0_server.py 已经启动：")
        print("  python mem0_server.py")
    except Exception as e:
        print(f"\n❌ 测试过程中出错：{e}")
        import traceback
        traceback.print_exc()

