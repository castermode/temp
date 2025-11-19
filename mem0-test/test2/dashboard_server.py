"""
FastAPI Web 服务器 - 提供查询数据库数据的 HTTP 接口

运行环境：conda activate py311
运行方式：python dashboard_server.py
测试方式：curl http://127.0.0.1:8888/query/db

# 接口1：查询sqlite
sqlite数据库路径:/Users/mhlee/.mem0/history.db
接口路径：/query/db
测试方式：curl http://127.0.0.1:8888/query/db

表名：history

表结构：
sqlite> PRAGMA table_info(history);
0|id|TEXT|0||1
1|memory_id|TEXT|0||0
2|old_memory|TEXT|0||0
3|new_memory|TEXT|0||0
4|event|TEXT|0||0
5|created_at|DATETIME|0||0
6|updated_at|DATETIME|0||0
7|is_deleted|INTEGER|0||0
8|actor_id|TEXT|0||0
9|role|TEXT|0||0

数据示例：
sqlite> .headers on
sqlite> select * from history;
id|memory_id|old_memory|new_memory|event|created_at|updated_at|is_deleted|actor_id|role
89dba432-7bb2-4c91-927d-47a80daba4f6|8367001d-f349-41e6-85d2-d5ad41c14393||喜欢吃苹果|ADD|2025-11-10T01:17:36.984254-08:00||0||
b1536858-c47e-47fe-a7ba-3856f72dd1f4|9783a0e2-6273-418d-a20e-d58289383700||苹果很甜|ADD|2025-11-10T01:17:36.986940-08:00||0||
30dd35e3-d309-4967-bdc3-325fc6163403|fd900668-1fed-4eef-9a80-3bd18a05cdb3||喜欢吃香蕉|ADD|2025-11-10T01:17:42.508086-08:00||0||
2c6cb1ba-23d4-4cec-8957-6ea4dbe4a329|948929fe-3783-4632-95a1-ba4d1f4f72cb||喜欢吃橘子|ADD|2025-11-10T01:17:48.091644-08:00||0||
4af52f75-8374-41ce-9950-475b3b0711d2|3633a14d-a133-4cec-954e-e1c8fcfff657||橘子富含营养|ADD|2025-11-10T01:17:48.096066-08:00||0||
deab2c76-e5e9-466e-b21a-3bd805eef498|8367001d-f349-41e6-85d2-d5ad41c14393|喜欢吃苹果||DELETE|||1||

测试结果展示：
curl http://127.0.0.1:8888/query/db
{"success":true,"count":6,"data":[{"id":"4af52f75-8374-41ce-9950-475b3b0711d2","memory_id":"3633a14d-a133-4cec-954e-e1c8fcfff657","old_memory":null,"new_memory":"橘子富含营养","event":"ADD","created_at":"2025-11-10T01:17:48.096066-08:00","updated_at":null,"is_deleted":0,"actor_id":null,"role":null},{"id":"2c6cb1ba-23d4-4cec-8957-6ea4dbe4a329","memory_id":"948929fe-3783-4632-95a1-ba4d1f4f72cb","old_memory":null,"new_memory":"喜欢吃橘子","event":"ADD","created_at":"2025-11-10T01:17:48.091644-08:00","updated_at":null,"is_deleted":0,"actor_id":null,"role":null},{"id":"30dd35e3-d309-4967-bdc3-325fc6163403","memory_id":"fd900668-1fed-4eef-9a80-3bd18a05cdb3","old_memory":null,"new_memory":"喜欢吃香蕉","event":"ADD","created_at":"2025-11-10T01:17:42.508086-08:00","updated_at":null,"is_deleted":0,"actor_id":null,"role":null},{"id":"b1536858-c47e-47fe-a7ba-3856f72dd1f4","memory_id":"9783a0e2-6273-418d-a20e-d58289383700","old_memory":null,"new_memory":"苹果很甜","event":"ADD","created_at":"2025-11-10T01:17:36.986940-08:00","updated_at":null,"is_deleted":0,"actor_id":null,"role":null},{"id":"89dba432-7bb2-4c91-927d-47a80daba4f6","memory_id":"8367001d-f349-41e6-85d2-d5ad41c14393","old_memory":null,"new_memory":"喜欢吃苹果","event":"ADD","created_at":"2025-11-10T01:17:36.984254-08:00","updated_at":null,"is_deleted":0,"actor_id":null,"role":null},{"id":"deab2c76-e5e9-466e-b21a-3bd805eef498","memory_id":"8367001d-f349-41e6-85d2-d5ad41c14393","old_memory":"喜欢吃苹果","new_memory":null,"event":"DELETE","created_at":null,"updated_at":null,"is_deleted":1,"actor_id":null,"role":null}]}






# 接口2：查询向量数据库 qdrant
qdrant:/Users/mhlee/Work/dev/ai-copilot/mem0-test/test2/memorydb/vector
接口路径：/query/vectordb
测试方式：curl http://127.0.0.1:8888/query/vectordb

集合名：mem0

集合配置
  向量大小: 1536
  距离度量: Cosine
  点数量: 4
  索引阈值: 20000

Payload Schema：
  未定义 schema（动态 schema）

数据示例：

--- 点 #1 ---
  ID: 3633a14d-a133-4cec-954e-e1c8fcfff657
  Payload:
    user_id: user_001
    data: 橘子富含营养
    hash: e390cef06dd982772f7e189f694461a7
    created_at: 2025-11-10T01:17:48.096066-08:00
  Vector: [维度: 1536, 前5个值: [-0.0182412788271904, -0.019237525761127472, -0.01887887716293335, 0.007008596323430538, 0.0651545375585556]...]

  --- 点 #2 ---
  ID: 948929fe-3783-4632-95a1-ba4d1f4f72cb
  Payload:
    user_id: user_001
    data: 喜欢吃橘子
    hash: 439fe21480d5552cfd8056c26cd6f0b3
    created_at: 2025-11-10T01:17:48.091644-08:00
  Vector: [维度: 1536, 前5个值: [0.056858308613300323, -0.06057596579194069, -0.019539576023817062, 0.003078002482652664, 0.05882648006081581]...]

  --- 点 #3 ---
  ID: 9783a0e2-6273-418d-a20e-d58289383700
  Payload:
    user_id: user_001
    data: 苹果很甜
    hash: 72882b81533eb182c5998d6f13199fe8
    created_at: 2025-11-10T01:17:36.986940-08:00
  Vector: [维度: 1536, 前5个值: [0.011416780762374401, -0.029202384874224663, -0.06520364433526993, 0.0008722573984414339, 0.009194860234856606]...]

  --- 点 #4 ---
  ID: fd900668-1fed-4eef-9a80-3bd18a05cdb3
  Payload:
    user_id: user_001
    data: 喜欢吃香蕉
    hash: 553cb759b0671e815b97f3aa5df02887
    created_at: 2025-11-10T01:17:42.508086-08:00
  Vector: [维度: 1536, 前5个值: [0.04354426637291908, -0.07675670087337494, -0.04655597358942032, 0.013918688520789146, 0.012998444028198719]...]

测试结果展示：
curl http://127.0.0.1:8888/query/vectordb
{"success":true,"count":4,"collection_info":{"name":1536,"points_count":4,"vectors_count":null},"data":[{"id":"3633a14d-a133-4cec-954e-e1c8fcfff657","payload":{"user_id":"user_001","data":"橘子富含营养","hash":"e390cef06dd982772f7e189f694461a7","created_at":"2025-11-10T01:17:48.096066-08:00"}},{"id":"948929fe-3783-4632-95a1-ba4d1f4f72cb","payload":{"user_id":"user_001","data":"喜欢吃橘子","hash":"439fe21480d5552cfd8056c26cd6f0b3","created_at":"2025-11-10T01:17:48.091644-08:00"}},{"id":"9783a0e2-6273-418d-a20e-d58289383700","payload":{"user_id":"user_001","data":"苹果很甜","hash":"72882b81533eb182c5998d6f13199fe8","created_at":"2025-11-10T01:17:36.986940-08:00"}},{"id":"fd900668-1fed-4eef-9a80-3bd18a05cdb3","payload":{"user_id":"user_001","data":"喜欢吃香蕉","hash":"553cb759b0671e815b97f3aa5df02887","created_at":"2025-11-10T01:17:42.508086-08:00"}}]}%







# 接口3：查询图数据库 kuzu
kuzu路径:/Users/mhlee/Work/dev/ai-copilot/mem0-test/test2/memorydb/graph/kemem_graph.db
接口路径：/query/graphdb
测试方式：curl http://127.0.0.1:8888/query/graphdb


【Entity 节点表】
----------------------------------------------------------------------------------------------------

表结构:

            CREATE NODE TABLE IF NOT EXISTS Entity(
                id SERIAL PRIMARY KEY,
                user_id STRING,
                agent_id STRING,
                run_id STRING,
                name STRING,
                mentions INT64,
                created TIMESTAMP,
                embedding FLOAT[]);


数据样例：所有节点数据:
----------------------------------------------------------------------------------------------------
ID                   User ID                        Agent ID             Run ID               Name                      Mentions   Created                  
----------------------------------------------------------------------------------------------------
{'offset': 0, 'table': 0} user_001                       NULL                 NULL                 user_id:_user_001         2          2025-11-10 09:15:26.130  
{'offset': 1, 'table': 0} user_001                       NULL                 NULL                 苹果                        5          2025-11-10 09:15:26.130  
{'offset': 2, 'table': 0} user_001                       NULL                 NULL                 甜                         1          2025-11-10 09:15:26.847  
{'offset': 3, 'table': 0} user_001                       NULL                 NULL                 我                         2          2025-11-10 09:17:39.232  
{'offset': 4, 'table': 0} user_001                       NULL                 NULL                 很甜                        1          2025-11-10 09:17:39.912  
{'offset': 5, 'table': 0} user_001                       NULL                 NULL                 香蕉                        2          2025-11-10 09:17:44.277  
{'offset': 6, 'table': 0} user_001                       NULL                 NULL                 能量                        1          2025-11-10 09:17:44.809  
{'offset': 7, 'table': 0} user_001                       NULL                 NULL                 橘子                        2          2025-11-10 09:17:49.488  
{'offset': 8, 'table': 0} user_001                       NULL                 NULL                 营养                        1          2025-11-10 09:17:50.114  
{'offset': 9, 'table': 0} user_001                       NULL                 NULL                 user_001                  1          2025-11-10 09:17:53.767  



【CONNECTED_TO 关系表】
----------------------------------------------------------------------------------------------------

表结构:

            CREATE REL TABLE IF NOT EXISTS CONNECTED_TO(
                FROM Entity TO Entity,
                name STRING,
                mentions INT64,
                created TIMESTAMP,
                updated TIMESTAMP
            );


数据样例：
所有关系数据:
----------------------------------------------------------------------------------------------------
Source                    Relationship              Destination               Mentions   Created                   Updated                  
----------------------------------------------------------------------------------------------------
user_id:_user_001         likes                     橘子                        1          2025-11-10 09:17:49.488   NULL                     
我                         likes                     香蕉                        1          2025-11-10 09:17:44.277   NULL                     
香蕉                        has                       能量                        1          2025-11-10 09:17:44.809   NULL                     
橘子                        contains                  营养                        1          2025-11-10 09:17:50.114   NULL                     
user_001                  dislikes                  苹果                        1          2025-11-10 09:17:53.767   NULL   


测试结果展示：
curl http://127.0.0.1:8888/query/graphdb
{"success":true,"nodes_count":10,"relationships_count":5,"data":{"nodes":[{"id":null,"user_id":"user_001","name":"user_id:_user_001","mentions":2,"created":"2025-11-10 09:15:26.130000"},{"id":"1","user_id":"user_001","name":"苹果","mentions":5,"created":"2025-11-10 09:15:26.130000"},{"id":"2","user_id":"user_001","name":"甜","mentions":1,"created":"2025-11-10 09:15:26.847000"},{"id":"3","user_id":"user_001","name":"我","mentions":2,"created":"2025-11-10 09:17:39.232000"},{"id":"4","user_id":"user_001","name":"很甜","mentions":1,"created":"2025-11-10 09:17:39.912000"},{"id":"5","user_id":"user_001","name":"香蕉","mentions":2,"created":"2025-11-10 09:17:44.277000"},{"id":"6","user_id":"user_001","name":"能量","mentions":1,"created":"2025-11-10 09:17:44.809000"},{"id":"7","user_id":"user_001","name":"橘子","mentions":2,"created":"2025-11-10 09:17:49.488000"},{"id":"8","user_id":"user_001","name":"营养","mentions":1,"created":"2025-11-10 09:17:50.114000"},{"id":"9","user_id":"user_001","name":"user_001","mentions":1,"created":"2025-11-10 09:17:53.767000"}],"relationships":[{"source":"user_id:_user_001","relationship":"likes","destination":"橘子","mentions":1,"created":"2025-11-10 09:17:49.488000","updated":null},{"source":"我","relationship":"likes","destination":"香蕉","mentions":1,"created":"2025-11-10 09:17:44.277000","updated":null},{"source":"香蕉","relationship":"has","destination":"能量","mentions":1,"created":"2025-11-10 09:17:44.809000","updated":null},{"source":"橘子","relationship":"contains","destination":"营养","mentions":1,"created":"2025-11-10 09:17:50.114000","updated":null},{"source":"user_001","relationship":"dislikes","destination":"苹果","mentions":1,"created":"2025-11-10 09:17:53.767000","updated":null}]}}%


"""

import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pathlib import Path
from qdrant_client import QdrantClient
import kuzu

# 创建 FastAPI 应用
app = FastAPI(title="Memory Dashboard API", description="查询记忆数据库的接口")

# 添加 CORS 中间件，允许前端页面访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# SQLite 数据库配置
DB_PATH = "/Users/mhlee/Work/dev/ai-copilot/mem0-test/test2/memorydb/history/history.db"
TABLE_NAME = "history"

# Qdrant 向量数据库配置
VECTOR_DB_PATH = "/Users/mhlee/Work/dev/ai-copilot/mem0-test/test2/memorydb/vector"
COLLECTION_NAME = "mem0"

# Kuzu 图数据库配置
GRAPH_DB_PATH = "/Users/mhlee/Work/dev/ai-copilot/mem0-test/test2/memorydb/graph/kemem_graph.db"


def get_db_connection():
    """获取 SQLite 数据库连接"""
    db_path = Path(DB_PATH)
    if not db_path.exists():
        raise FileNotFoundError(f"数据库文件不存在: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
    return conn


def get_vector_db_client():
    """获取 Qdrant 向量数据库客户端"""
    vector_db_path = Path(VECTOR_DB_PATH)
    if not vector_db_path.exists():
        raise FileNotFoundError(f"向量数据库目录不存在: {VECTOR_DB_PATH}")
    
    # 连接到本地 Qdrant 数据库
    client = QdrantClient(path=VECTOR_DB_PATH)
    return client


def get_graph_db_connection():
    """获取 Kuzu 图数据库连接"""
    graph_db_path = Path(GRAPH_DB_PATH)
    if not graph_db_path.exists():
        raise FileNotFoundError(f"图数据库目录不存在: {GRAPH_DB_PATH}")
    
    # 连接到 Kuzu 图数据库
    db = kuzu.Database(GRAPH_DB_PATH)
    conn = kuzu.Connection(db)
    return conn


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "message": "Memory Dashboard API",
        "endpoints": {
            "/query/db": "查询 SQLite history 表的所有数据",
            "/query/db?limit=10": "查询 history 表的前 10 条数据",
            "/query/db?event=ADD": "查询特定事件类型的数据",
            "/query/vectordb": "查询 Qdrant 向量数据库的所有数据",
            "/query/vectordb?limit=10": "查询向量数据库的前 10 条数据",
            "/query/vectordb?user_id=user_001": "查询特定用户的向量数据",
            "/query/graphdb": "查询 Kuzu 图数据库的所有节点和关系",
            "/query/graphdb?user_id=user_001": "查询特定用户的图数据",
        }
    }


@app.get("/query/db")
async def query_database(
    limit: int = None,
    event: str = None,
    memory_id: str = None
) -> JSONResponse:
    """
    查询 sqlite 数据库中的 history 表
    
    参数：
    - limit: 限制返回的记录数量
    - event: 过滤特定事件类型（如 ADD, DELETE, UPDATE）
    - memory_id: 过滤特定的 memory_id
    
    返回：
    - 查询结果的 JSON 列表
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建 SQL 查询
        query = f"SELECT * FROM {TABLE_NAME}"
        conditions = []
        params = []
        
        # 添加过滤条件
        if event:
            conditions.append("event = ?")
            params.append(event)
        
        if memory_id:
            conditions.append("memory_id = ?")
            params.append(memory_id)
        
        # 组合条件
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # 添加排序和限制
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        # 执行查询
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 转换为字典列表
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "memory_id": row["memory_id"],
                "old_memory": row["old_memory"],
                "new_memory": row["new_memory"],
                "event": row["event"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "is_deleted": row["is_deleted"],
                "actor_id": row["actor_id"],
                "role": row["role"]
            })
        
        conn.close()
        
        return JSONResponse(content={
            "success": True,
            "count": len(result),
            "data": result
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/query/db/stats")
async def query_statistics():
    """
    查询数据库统计信息
    
    返回：
    - 各类事件的数量统计
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 统计总记录数
        cursor.execute(f"SELECT COUNT(*) as total FROM {TABLE_NAME}")
        total = cursor.fetchone()["total"]
        
        # 按事件类型统计
        cursor.execute(f"""
            SELECT event, COUNT(*) as count 
            FROM {TABLE_NAME} 
            GROUP BY event
        """)
        event_stats = {row["event"]: row["count"] for row in cursor.fetchall()}
        
        # 统计删除的记录数
        cursor.execute(f"SELECT COUNT(*) as deleted FROM {TABLE_NAME} WHERE is_deleted = 1")
        deleted = cursor.fetchone()["deleted"]
        
        conn.close()
        
        return JSONResponse(content={
            "success": True,
            "statistics": {
                "total_records": total,
                "deleted_records": deleted,
                "event_counts": event_stats
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询统计信息失败: {str(e)}")


@app.get("/query/vectordb")
async def query_vectordb(
    limit: int = None,
    user_id: str = None,
    include_vectors: bool = False
) -> JSONResponse:
    """
    查询 Qdrant 向量数据库中的数据
    
    参数：
    - limit: 限制返回的记录数量
    - user_id: 过滤特定用户的数据
    - include_vectors: 是否包含向量数据（默认不包含，因为向量数据很大）
    
    返回：
    - 查询结果的 JSON 列表
    """
    try:
        # 获取 Qdrant 客户端
        client = get_vector_db_client()
        
        # 检查集合是否存在
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            raise HTTPException(
                status_code=404, 
                detail=f"集合 '{COLLECTION_NAME}' 不存在。可用集合: {collection_names}"
            )
        
        # 获取集合信息
        collection_info = client.get_collection(COLLECTION_NAME)
        
        # 构建过滤条件
        scroll_filter = None
        if user_id:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
        
        # 滚动获取所有点（或限制数量）
        scroll_limit = limit if limit else 100  # 默认最多返回 100 条
        
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=scroll_filter,
            limit=scroll_limit,
            with_vectors=include_vectors,
            with_payload=True
        )
        
        # 格式化结果
        result = []
        for point in points:
            point_data = {
                "id": str(point.id),
                "payload": point.payload if point.payload else {}
            }
            
            # 如果需要包含向量，添加向量信息
            if include_vectors and point.vector:
                if isinstance(point.vector, list):
                    # 向量是列表
                    vector_data = point.vector
                    point_data["vector"] = {
                        "dimension": len(vector_data),
                        "first_5_values": vector_data[:5],
                        "full_vector": vector_data if len(vector_data) <= 100 else None  # 只有小向量才返回全部
                    }
                elif isinstance(point.vector, dict):
                    # 命名向量
                    point_data["vectors"] = {}
                    for name, vec in point.vector.items():
                        point_data["vectors"][name] = {
                            "dimension": len(vec),
                            "first_5_values": vec[:5]
                        }
            
            result.append(point_data)
        
        return JSONResponse(content={
            "success": True,
            "count": len(result),
            "collection_info": {
                "name": collection_info.config.params.vectors.size if hasattr(collection_info.config.params.vectors, 'size') else None,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else None
            },
            "data": result
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询向量数据库失败: {str(e)}")


@app.get("/query/vectordb/stats")
async def query_vectordb_statistics():
    """
    查询向量数据库统计信息
    
    返回：
    - 集合配置和统计信息
    """
    try:
        client = get_vector_db_client()
        
        # 检查集合是否存在
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"集合 '{COLLECTION_NAME}' 不存在"
            )
        
        # 获取集合详细信息
        collection_info = client.get_collection(COLLECTION_NAME)
        
        # 提取配置信息
        config = collection_info.config
        params = config.params
        
        stats = {
            "collection_name": COLLECTION_NAME,
            "points_count": collection_info.points_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count if hasattr(collection_info, 'indexed_vectors_count') else None,
            "segments_count": len(collection_info.payload_schema) if hasattr(collection_info, 'payload_schema') else None,
            "config": {
                "vector_size": params.vectors.size if hasattr(params.vectors, 'size') else None,
                "distance": params.vectors.distance.name if hasattr(params.vectors, 'distance') else None,
            },
            "payload_schema": collection_info.payload_schema if hasattr(collection_info, 'payload_schema') else {}
        }
        
        return JSONResponse(content={
            "success": True,
            "statistics": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询向量数据库统计信息失败: {str(e)}")


@app.get("/query/graphdb")
async def query_graphdb(
    user_id: str = None,
    limit: int = None
) -> JSONResponse:
    """
    查询 Kuzu 图数据库中的节点和关系
    
    参数：
    - user_id: 过滤特定用户的数据
    - limit: 限制返回的记录数量
    
    返回：
    - 节点和关系的 JSON 数据
    """
    try:
        # 获取图数据库连接
        conn = get_graph_db_connection()
        
        # 查询节点（Entity）
        nodes_query = "MATCH (e:Entity) RETURN e.id AS id, e.user_id AS user_id, e.name AS name, e.mentions AS mentions, e.created AS created"
        
        if user_id:
            nodes_query = f"MATCH (e:Entity) WHERE e.user_id = '{user_id}' RETURN e.id AS id, e.user_id AS user_id, e.name AS name, e.mentions AS mentions, e.created AS created"
        
        if limit:
            nodes_query += f" LIMIT {limit}"
        
        # 执行节点查询
        nodes_result = conn.execute(nodes_query)
        nodes = []
        while nodes_result.has_next():
            row = nodes_result.get_next()
            nodes.append({
                "id": str(row[0]) if row[0] else None,
                "user_id": row[1] if row[1] else None,
                "name": row[2] if row[2] else None,
                "mentions": int(row[3]) if row[3] else 0,
                "created": str(row[4]) if row[4] else None
            })
        
        # 查询关系（CONNECTED_TO）
        relationships_query = """
            MATCH (e1:Entity)-[r:CONNECTED_TO]->(e2:Entity) 
            RETURN e1.name AS source, r.name AS relationship, e2.name AS destination, 
                   r.mentions AS mentions, r.created AS created, r.updated AS updated
        """
        
        if user_id:
            relationships_query = f"""
                MATCH (e1:Entity)-[r:CONNECTED_TO]->(e2:Entity) 
                WHERE e1.user_id = '{user_id}'
                RETURN e1.name AS source, r.name AS relationship, e2.name AS destination, 
                       r.mentions AS mentions, r.created AS created, r.updated AS updated
            """
        
        if limit:
            relationships_query += f" LIMIT {limit}"
        
        # 执行关系查询
        relationships_result = conn.execute(relationships_query)
        relationships = []
        while relationships_result.has_next():
            row = relationships_result.get_next()
            relationships.append({
                "source": row[0] if row[0] else None,
                "relationship": row[1] if row[1] else None,
                "destination": row[2] if row[2] else None,
                "mentions": int(row[3]) if row[3] else 0,
                "created": str(row[4]) if row[4] else None,
                "updated": str(row[5]) if row[5] else None
            })
        
        return JSONResponse(content={
            "success": True,
            "nodes_count": len(nodes),
            "relationships_count": len(relationships),
            "data": {
                "nodes": nodes,
                "relationships": relationships
            }
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询图数据库失败: {str(e)}")


@app.get("/query/graphdb/stats")
async def query_graphdb_statistics():
    """
    查询图数据库统计信息
    
    返回：
    - 节点和关系的统计信息
    """
    try:
        conn = get_graph_db_connection()
        
        # 统计节点总数
        nodes_count_result = conn.execute("MATCH (e:Entity) RETURN COUNT(*) AS count")
        nodes_count = 0
        if nodes_count_result.has_next():
            nodes_count = int(nodes_count_result.get_next()[0])
        
        # 统计关系总数
        relationships_count_result = conn.execute("MATCH ()-[r:CONNECTED_TO]->() RETURN COUNT(*) AS count")
        relationships_count = 0
        if relationships_count_result.has_next():
            relationships_count = int(relationships_count_result.get_next()[0])
        
        # 统计不同用户数
        users_result = conn.execute("MATCH (e:Entity) RETURN DISTINCT e.user_id")
        users = set()
        while users_result.has_next():
            user = users_result.get_next()[0]
            if user:
                users.add(user)
        
        # 统计不同关系类型
        relationship_types_result = conn.execute("MATCH ()-[r:CONNECTED_TO]->() RETURN r.name, COUNT(*) AS count")
        relationship_types = {}
        while relationship_types_result.has_next():
            row = relationship_types_result.get_next()
            rel_type = row[0] if row[0] else "unknown"
            count = int(row[1])
            relationship_types[rel_type] = count
        
        return JSONResponse(content={
            "success": True,
            "statistics": {
                "nodes_count": nodes_count,
                "relationships_count": relationships_count,
                "users_count": len(users),
                "relationship_types": relationship_types
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询图数据库统计信息失败: {str(e)}")


if __name__ == "__main__":
    print("启动 Memory Dashboard API 服务器...")
    print(f"SQLite 数据库路径: {DB_PATH}")
    print(f"Qdrant 向量数据库路径: {VECTOR_DB_PATH}")
    print(f"Kuzu 图数据库路径: {GRAPH_DB_PATH}")
    print(f"访问地址: http://127.0.0.1:8888")
    print(f"API 文档: http://127.0.0.1:8888/docs")
    print("\n可用接口:")
    print("  - GET /query/db              : 查询 SQLite 历史记录")
    print("  - GET /query/db/stats        : SQLite 统计信息")
    print("  - GET /query/vectordb        : 查询向量数据库")
    print("  - GET /query/vectordb/stats  : 向量数据库统计信息")
    print("  - GET /query/graphdb         : 查询图数据库")
    print("  - GET /query/graphdb/stats   : 图数据库统计信息")
    
    uvicorn.run(app, host="127.0.0.1", port=8888)