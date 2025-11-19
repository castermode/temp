"""
使用 mem0 1.0.0 添加记忆的示例代码
使用 Azure OpenAI 作为 LLM 和 Embedding 模型
运行环境为 conda activate py311
"""

import argparse
import json
import os
from mem0 import Memory


# 修改代码，通过命令行参数 --infer 决定是否启用add方法的infer参数
# 如果有 --infer 参数，则设置add方法的infer参数为True
# 如果没有 --infer 参数，则设置add方法的infer参数为False

os.environ["MEM0_TELEMETRY"] = "false"

# 解析命令行参数
parser = argparse.ArgumentParser(
    description='KeMem 记忆管理测试工具',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
使用示例:
  # 使用默认配置（仅向量存储）
  python kemem_test.py
  
  # 启用图数据库
  python kemem_test.py --graph
  
  # 启用 infer 参数（推理记忆内容）
  python kemem_test.py --infer
  
  # 指定对话文件
  python kemem_test.py --chats ./chats.txt
  
  # 使用自定义 update_memory_prompt
  python kemem_test.py --update-memory-prompt ./my_update_prompt.txt
  
  # 指定用户 ID
  python kemem_test.py --user-id user_002
  
  # 组合使用（启用图数据库 + infer + 自定义配置）
  python kemem_test.py --graph --infer --chats ./chats.txt --update-memory-prompt ./my_update_prompt.txt --user-id user_002
    '''
)

parser.add_argument(
    '--update-memory-prompt',
    type=str,
    default=None,
    metavar='FILE',
    help='自定义 update_memory_prompt 文件路径（默认使用 Mem0 内置 prompt）'
)

parser.add_argument(
    '--user-id',
    type=str,
    default='user_001',
    metavar='ID',
    help='用户 ID，用于隔离不同用户的记忆（默认: user_001）'
)

parser.add_argument(
    '--chats',
    type=str,
    default='chats.txt',
    metavar='FILE',
    help='包含对话记录的文件路径（默认: chats.txt）'
)

parser.add_argument(
    '--graph',
    action='store_true',
    help='启用图数据库（Kuzu）来存储实体关系'
)

parser.add_argument(
    '--infer',
    action='store_true',
    help='启用 add 方法的 infer 参数，用于推理记忆内容'
)

args = parser.parse_args()

# 读取自定义 prompt（如果提供）
MY_UPDATE_PROMPT = None
if args.update_memory_prompt:
    try:
        with open(args.update_memory_prompt, 'r', encoding='utf-8') as f:
            MY_UPDATE_PROMPT = f.read()
        print(f"已加载自定义 update_memory_prompt: {args.update_memory_prompt}")
    except FileNotFoundError:
        print(f"警告：找不到文件 {args.update_memory_prompt}，将使用默认 prompt")
    except Exception as e:
        print(f"警告：读取文件时出错 {e}，将使用默认 prompt")

#配置 Azure OpenAI 模型
config = {
#LLM 配置 - gpt - 4.1 - nano
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
#Embedding 配置 - text - embedding - 3 - small
    "embedder": {
        "provider": "azure_openai",
        "config": {
            "model": "text-embedding-3-small",
            "embedding_dims": 1536,  # text-embedding-3-small 的默认维度
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
    }
}

# 如果提供了自定义 prompt，则添加到配置中
if MY_UPDATE_PROMPT:
    config["custom_update_memory_prompt"] = MY_UPDATE_PROMPT
    print("使用自定义 update_memory_prompt")
else:
    print("使用默认 update_memory_prompt")

# 如果启用了图数据库，则添加到配置中
if args.graph:
    config["graph_store"] = {
        "provider": "kuzu",
        "config": {
            "db": "./memorydb/graph/kemem_graph.db"  # 使用本地文件存储图数据
        }
    }
    print("✅ 已启用图数据库（Kuzu）")
else:
    print("⚪ 未启用图数据库（仅使用向量存储）")

#创建 Memory 实例
print("创建 Memory 实例...")
memory = Memory.from_config(config_dict=config)

# 显示是否启用了图数据库
if hasattr(memory, 'enable_graph'):
    print(f"图数据库状态: {memory.enable_graph}")


# 从外部文件 chats.txt 中读取对话记录并添加到记忆中
# chats.txt 每行一条记忆（JSON 格式）

print(f"\n从文件读取对话记录: {args.chats}")
print("=" * 60)

# 检查文件是否存在
if not os.path.exists(args.chats):
    print(f"错误：找不到文件 {args.chats}")
    print("请确保 chats.txt 文件存在于当前目录")
    exit(1)

# 读取并处理每一行对话记录
try:
    with open(args.chats, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"共读取到 {len(lines)} 条对话记录\n")
    
    for idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line:  # 跳过空行
            continue
        
        try:
            # 解析 JSON 格式的对话
            messages = json.loads(line)
            
            print(f"[{idx}/{len(lines)}] 添加记忆：")
            # 显示对话内容
            for msg in messages:
                role = msg.get('role', '')
                content = msg.get('content', '')
                print(f"  {role}: {content}")
            
            # 添加到记忆中
            result = memory.add(
                messages=messages,
                user_id=args.user_id,
                infer=args.infer
            )
            
            # 如果启用了图数据库，显示图关系信息
            if args.graph and result.get('relations'):
                relations = result['relations']
                if isinstance(relations, dict):
                    added = relations.get('added_entities', [])
                    if added:
                        print(f"\n  🔗 新增图关系: {len(added)} 条")
                        for rel in added[:5]:
                            if isinstance(rel, dict):
                                print(f"     {rel.get('source')} --[{rel.get('relationship')}]--> {rel.get('target')}")
            
            # 每次添加后查看所有记忆
            print(f"\n  当前所有记忆：")
            all_memories = memory.get_all(user_id=args.user_id)
            if all_memories and all_memories.get('results'):
                for mem in all_memories['results']:
                    print(f"    - [{mem['id'][:8]}...] {mem['memory']}")
            else:
                print("    (无记忆)")
            print("-" * 60)
            
        except json.JSONDecodeError as e:
            print(f"  警告：第 {idx} 行 JSON 解析失败: {e}")
            print(f"  内容: {line}")
            print("-" * 60)
            continue
        except Exception as e:
            print(f"  错误：添加第 {idx} 行记忆时出错: {e}")
            print("-" * 60)
            continue
    
    print("\n所有对话记录处理完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"错误：读取文件时出错: {e}")
    exit(1)










# 搜索记忆
print("\n\n" + "=" * 60)
print("开始搜索记忆")
print("=" * 60)

queries = [
    "我喜欢吃什么",
    "我喜欢干什么",
    "关于苹果"
]

for query_msg in queries:
    print(f"\n搜索查询：{query_msg}")
    print("-" * 40)
    result = memory.search(
        query=query_msg,
        user_id=args.user_id
    )
    
    # 格式化输出搜索结果
    if result and result.get('results'):
        print(f"找到 {len(result['results'])} 条相关记忆：")
        for idx, mem in enumerate(result['results'], 1):
            print(f"  {idx}. {mem.get('memory', 'N/A')}")
            if 'score' in mem:
                print(f"     (相关度: {mem['score']:.4f})")
    else:
        print("  未找到相关记忆")
    
    # 如果启用了图数据库，显示图关系
    if args.graph and result.get('relations'):
        relations = result['relations']
        if isinstance(relations, list) and relations:
            print(f"\n  🔗 相关图关系: {len(relations)} 条")
            for rel in relations[:5]:
                if isinstance(rel, dict):
                    source = rel.get('source', 'N/A')
                    relationship = rel.get('relationship', rel.get('relation', 'N/A'))
                    destination = rel.get('destination', rel.get('target', 'N/A'))
                    print(f"     {source} --[{relationship}]--> {destination}")
    
    print()

print("=" * 60)
print("测试完成！")
print("=" * 60)