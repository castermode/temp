"""
测试 mem0 的 search 功能
使用与 kemem_test.py 相同的配置
运行环境为 conda activate py311
"""

import json
from mem0 import Memory
import os

# 配置 Azure OpenAI 模型（与 kemem_test.py 相同）
config = {
    # LLM 配置 - gpt-4.1-nano       
    "llm": {
        "provider": "azure_openai",
        "config": {
            "model": "gpt-4.1-nano",
            "azure_kwargs": {
                "api_key": os.getenv("GPT_41_NANO_KEY"),
                "azure_deployment": "gpt-4.1-nano",
                "azure_endpoint": "https://bk-us-2.openai.azure.com",
                "api_version": "2025-01-01-preview",
            }
        }
    },
    # Embedding 配置 - text-embedding-3-small
    "embedder": {
        "provider": "azure_openai",
        "config": {
            "model": "text-embedding-3-small",
            "embedding_dims": 1536,
            "azure_kwargs": {
                "api_key": os.getenv("TEXT_EMBEDDING_3_SMALL"),
                "azure_deployment": "text-embedding-3-small",
                "azure_endpoint": "https://bk-cloud.openai.azure.com",
                "api_version": "2023-05-15",
            }
        }
    },
    # 向量存储配置 - 明确指定存储路径
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": "./memorydb/vector",  # 使用本地目录存储向量数据
            "on_disk": True  # 启用持久化存储，防止每次初始化时删除数据
        }
    },
    "graph_store": {
        "provider": "kuzu",
        "config": {
            "db": "./memorydb/graph/kemem_graph.db"  # 使用本地文件存储图数据
        }
    }
}

# 创建 Memory 实例
print("创建 Memory 实例...")
memory = Memory.from_config(config_dict=config)

# 测试搜索功能
print("\n" + "=" * 60)
print("测试搜索功能")
print("=" * 60)

# 搜索查询
query = "我喜欢吃橘子吗"
user_id = "user_001"

print(f"\n搜索查询：{query}")
print(f"用户 ID：{user_id}")
print("-" * 60)

# 执行搜索
try:
    result = memory.search(
        query=query,
        user_id=user_id
    )
    
    print("=" * 60)
    print("原始结果（格式化）：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)


    # 显示搜索结果
    if result and result.get('results'):
        print(f"\n✅ 找到 {len(result['results'])} 条相关记忆：\n")
        for idx, mem in enumerate(result['results'], 1):
            print(f"{idx}. {mem.get('memory', 'N/A')}")
            if 'score' in mem:
                print(f"   相关度分数: {mem['score']:.4f}")
            if 'id' in mem:
                print(f"   记忆 ID: {mem['id']}")
            print()
        
        # 显示图数据库关系（如果启用了图数据库）
        if result.get('relations'):
            relations = result['relations']
            print("\n🔗 相关图关系：")
            if isinstance(relations, list) and relations:
                print(f"   找到 {len(relations)} 条关系\n")
                for idx, rel in enumerate(relations, 1):
                    if isinstance(rel, dict):
                        source = rel.get('source', 'N/A')
                        relationship = rel.get('relationship', rel.get('relation', 'N/A'))
                        destination = rel.get('destination', rel.get('target', 'N/A'))
                        print(f"   {idx}. {source} --[{relationship}]--> {destination}")
            else:
                print("   无图关系数据")
            print()
    
    elif result and result.get('relations'):
        # 没有向量结果，但有图关系
        print("\n⚪ 未找到向量记忆，但找到图关系：")
        relations = result['relations']
        if isinstance(relations, list) and relations:
            print(f"   找到 {len(relations)} 条关系\n")
            for idx, rel in enumerate(relations, 1):
                if isinstance(rel, dict):
                    source = rel.get('source', 'N/A')
                    relationship = rel.get('relationship', rel.get('relation', 'N/A'))
                    destination = rel.get('destination', rel.get('target', 'N/A'))
                    print(f"   {idx}. {source} --[{relationship}]--> {destination}")
        print()
    
    else:
        print("\n❌ 未找到相关记忆")
        
except Exception as e:
    print(f"\n❌ 搜索时发生错误：")
    print(f"   错误类型: {type(e).__name__}")
    print(f"   错误信息: {str(e)}")
    import traceback
    print("\n详细错误信息：")
    traceback.print_exc()

print("=" * 60)
print("搜索测试完成！")
print("=" * 60)