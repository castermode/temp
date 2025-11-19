"""
编写代码，打印kuzu图数据库的表结构与所有数据
路径为 "./memorydb/graph/kemem_graph.db"
运行环境为 conda activate py311
"""

import kuzu
import os
from datetime import datetime


def check_kuzu_db():
    """检查并打印Kuzu图数据库的表结构与所有数据"""
    db_path = "./memorydb/graph/kemem_graph.db"
    
    # 检查数据库目录是否存在
    if not os.path.exists(db_path):
        print(f"数据库目录不存在: {db_path}")
        return
    
    print(f"数据库路径: {db_path}")
    print("=" * 100)
    
    try:
        # 连接到Kuzu数据库
        db = kuzu.Database(db_path)
        conn = kuzu.Connection(db)
        
        # 1. 获取所有表（节点表和关系表）
        print("\n【数据库表列表】")
        print("-" * 100)
        
        # 获取所有节点表
        node_tables_result = conn.execute("CALL show_tables() RETURN *;")
        tables_info = []
        while node_tables_result.has_next():
            row = node_tables_result.get_next()
            tables_info.append(row)
        
        if not tables_info:
            print("数据库中没有表")
            return
        
        print(f"找到 {len(tables_info)} 个表:")
        for i, table in enumerate(tables_info, 1):
            print(f"  {i}. {table}")
        
        # 2. 打印节点表 (Entity) 的结构和数据
        print("\n" + "=" * 100)
        print("\n【Entity 节点表】")
        print("-" * 100)
        
        # 打印表结构 (Schema)
        print("\n表结构:")
        try:
            schema_query = """
            CREATE NODE TABLE IF NOT EXISTS Entity(
                id SERIAL PRIMARY KEY,
                user_id STRING,
                agent_id STRING,
                run_id STRING,
                name STRING,
                mentions INT64,
                created TIMESTAMP,
                embedding FLOAT[]);
            """
            print(schema_query)
        except Exception as e:
            print(f"获取表结构失败: {e}")
        
        # 统计节点总数
        try:
            count_result = conn.execute("MATCH (n:Entity) RETURN count(*) as count;")
            count_row = count_result.get_next()
            node_count = count_row[0]
            print(f"\n节点总数: {node_count}")
        except Exception as e:
            print(f"统计节点失败: {e}")
            node_count = 0
        
        # 打印所有节点数据
        if node_count > 0:
            print("\n所有节点数据:")
            print("-" * 100)
            try:
                nodes_result = conn.execute("""
                    MATCH (n:Entity) 
                    RETURN 
                        id(n) as id,
                        n.user_id as user_id, 
                        n.agent_id as agent_id,
                        n.run_id as run_id,
                        n.name as name, 
                        n.mentions as mentions,
                        n.created as created
                    LIMIT 1000;
                """)
                
                # 打印表头
                print(f"{'ID':<20} {'User ID':<30} {'Agent ID':<20} {'Run ID':<20} {'Name':<25} {'Mentions':<10} {'Created':<25}")
                print("-" * 100)
                
                # 打印每个节点
                node_num = 0
                while nodes_result.has_next():
                    node = nodes_result.get_next()
                    node_num += 1
                    node_id = str(node[0]) if node[0] else "NULL"
                    user_id = str(node[1])[:28] if node[1] else "NULL"
                    agent_id = str(node[2])[:18] if node[2] else "NULL"
                    run_id = str(node[3])[:18] if node[3] else "NULL"
                    name = str(node[4])[:23] if node[4] else "NULL"
                    mentions = str(node[5]) if node[5] is not None else "NULL"
                    created = str(node[6])[:23] if node[6] else "NULL"
                    
                    print(f"{node_id:<20} {user_id:<30} {agent_id:<20} {run_id:<20} {name:<25} {mentions:<10} {created:<25}")
                
                print(f"\n共显示 {node_num} 个节点")
                    
            except Exception as e:
                print(f"查询节点数据失败: {e}")
        
        # 3. 打印关系表 (CONNECTED_TO) 的结构和数据
        print("\n" + "=" * 100)
        print("\n【CONNECTED_TO 关系表】")
        print("-" * 100)
        
        # 打印表结构
        print("\n表结构:")
        try:
            schema_query = """
            CREATE REL TABLE IF NOT EXISTS CONNECTED_TO(
                FROM Entity TO Entity,
                name STRING,
                mentions INT64,
                created TIMESTAMP,
                updated TIMESTAMP
            );
            """
            print(schema_query)
        except Exception as e:
            print(f"获取关系表结构失败: {e}")
        
        # 统计关系总数
        try:
            count_result = conn.execute("MATCH ()-[r:CONNECTED_TO]->() RETURN count(*) as count;")
            count_row = count_result.get_next()
            rel_count = count_row[0]
            print(f"\n关系总数: {rel_count}")
        except Exception as e:
            print(f"统计关系失败: {e}")
            rel_count = 0
        
        # 打印所有关系数据
        if rel_count > 0:
            print("\n所有关系数据:")
            print("-" * 100)
            try:
                rels_result = conn.execute("""
                    MATCH (n:Entity)-[r:CONNECTED_TO]->(m:Entity) 
                    RETURN 
                        n.name as source,
                        r.name as relationship, 
                        m.name as destination,
                        r.mentions as mentions,
                        r.created as created,
                        r.updated as updated
                    LIMIT 1000;
                """)
                
                # 打印表头
                print(f"{'Source':<25} {'Relationship':<25} {'Destination':<25} {'Mentions':<10} {'Created':<25} {'Updated':<25}")
                print("-" * 100)
                
                # 打印每个关系
                rel_num = 0
                while rels_result.has_next():
                    rel = rels_result.get_next()
                    rel_num += 1
                    source = str(rel[0])[:23] if rel[0] else "NULL"
                    relationship = str(rel[1])[:23] if rel[1] else "NULL"
                    destination = str(rel[2])[:23] if rel[2] else "NULL"
                    mentions = str(rel[3]) if rel[3] is not None else "NULL"
                    created = str(rel[4])[:23] if rel[4] else "NULL"
                    updated = str(rel[5])[:23] if rel[5] else "NULL"
                    
                    print(f"{source:<25} {relationship:<25} {destination:<25} {mentions:<10} {created:<25} {updated:<25}")
                
                print(f"\n共显示 {rel_num} 个关系")
                    
            except Exception as e:
                print(f"查询关系数据失败: {e}")
        
        # 4. 额外统计信息
        print("\n" + "=" * 100)
        print("\n【数据统计】")
        print("-" * 100)
        
        # 按 user_id 统计
        try:
            user_result = conn.execute("""
                MATCH (n:Entity) 
                RETURN n.user_id as user_id, count(*) as count 
                ORDER BY count DESC;
            """)
            print("\n按 user_id 统计节点数:")
            while user_result.has_next():
                row = user_result.get_next()
                user_id = row[0] if row[0] else "NULL"
                count = row[1]
                print(f"  {user_id}: {count} 个节点")
        except Exception as e:
            print(f"统计用户节点数失败: {e}")
        
        # 按 name 统计最常提及的实体
        try:
            name_result = conn.execute("""
                MATCH (n:Entity) 
                WHERE n.mentions IS NOT NULL
                RETURN n.name as name, n.mentions as mentions 
                ORDER BY n.mentions DESC
                LIMIT 10;
            """)
            print("\n最常提及的实体 (Top 10):")
            while name_result.has_next():
                row = name_result.get_next()
                name = row[0] if row[0] else "NULL"
                mentions = row[1] if row[1] is not None else 0
                print(f"  {name}: {mentions} 次")
        except Exception as e:
            print(f"统计实体提及次数失败: {e}")
        
        print("\n" + "=" * 100)
        print("\n数据库检查完成")
        
    except Exception as e:
        print(f"数据库操作错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_kuzu_db()
