"""
编写代码，打印Qdrant向量数据库的表结构与所有数据
路径为 "/tmp/qdrant"
运行环境为 conda activate py311
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json

def print_qdrant_info(qdrant_path="./memorydb/vector"):
    """打印 Qdrant 数据库的表结构和所有数据"""
    
    # 连接到本地 Qdrant 数据库
    client = QdrantClient(path=qdrant_path)
    
    print("=" * 80)
    print("Qdrant 向量数据库信息")
    print(f"数据库路径: {qdrant_path}")
    print("=" * 80)
    
    # 获取所有集合（collections）
    collections = client.get_collections()
    
    if not collections.collections:
        print("\n数据库中没有集合（collections）")
        return
    
    print(f"\n找到 {len(collections.collections)} 个集合\n")
    
    # 遍历每个集合
    for collection in collections.collections:
        collection_name = collection.name
        print("\n" + "=" * 80)
        print(f"集合名称: {collection_name}")
        print("=" * 80)
        
        # 获取集合信息
        collection_info = client.get_collection(collection_name)
        
        # 打印集合配置信息
        print("\n【集合配置】")
        print(f"  向量大小: {collection_info.config.params.vectors.size if hasattr(collection_info.config.params.vectors, 'size') else 'N/A'}")
        print(f"  距离度量: {collection_info.config.params.vectors.distance if hasattr(collection_info.config.params.vectors, 'distance') else 'N/A'}")
        print(f"  点数量: {collection_info.points_count}")
        print(f"  索引阈值: {collection_info.config.optimizer_config.indexing_threshold}")
        
        # 打印 payload schema
        if collection_info.payload_schema:
            print("\n【Payload Schema】")
            for key, value in collection_info.payload_schema.items():
                print(f"  {key}: {value}")
        else:
            print("\n【Payload Schema】")
            print("  未定义 schema（动态 schema）")
        
        # 获取并打印所有数据点
        print("\n【数据点详情】")
        
        # 滚动获取所有点
        offset = None
        total_points = 0
        
        while True:
            # 每次获取 100 个点
            records, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )
            
            if not records:
                break
            
            for point in records:
                total_points += 1
                print(f"\n  --- 点 #{total_points} ---")
                print(f"  ID: {point.id}")
                
                # 打印 payload
                if point.payload:
                    print(f"  Payload:")
                    for key, value in point.payload.items():
                        # 如果值太长，截断显示
                        if isinstance(value, str) and len(value) > 100:
                            print(f"    {key}: {value[:100]}...")
                        else:
                            print(f"    {key}: {value}")
                
                # 打印向量（通常很长，只显示维度和前几个值）
                if point.vector:
                    if isinstance(point.vector, list):
                        print(f"  Vector: [维度: {len(point.vector)}, 前5个值: {point.vector[:5]}...]")
                    elif isinstance(point.vector, dict):
                        print(f"  Vector (命名向量):")
                        for vec_name, vec_data in point.vector.items():
                            if isinstance(vec_data, list):
                                print(f"    {vec_name}: [维度: {len(vec_data)}, 前5个值: {vec_data[:5]}...]")
            
            # 检查是否有更多数据
            if next_offset is None:
                break
            offset = next_offset
        
        print(f"\n  总共 {total_points} 个数据点")
    
    print("\n" + "=" * 80)
    print("数据库信息打印完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        print_qdrant_info("./memorydb/vector")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()