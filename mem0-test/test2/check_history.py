"""
编写代码，打印sqlite数据库的history表结构与所有数据
路径为 "~/.mem0/history.db"
运行环境为 conda activate py311
"""

import sqlite3
import os
from pathlib import Path

def check_sqlite_db():
    # 扩展用户目录路径
    db_path = os.path.expanduser("~/.mem0/history.db")
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库路径: {db_path}")
    print("=" * 80)
    
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 打印表结构
        print("\n【History 表结构】")
        print("-" * 80)
        cursor.execute("PRAGMA table_info(history)")
        columns = cursor.fetchall()
        
        if not columns:
            print("history 表不存在")
            return
        
        print(f"{'列ID':<8} {'列名':<20} {'数据类型':<15} {'非空':<8} {'默认值':<15} {'主键':<8}")
        print("-" * 80)
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            print(f"{cid:<8} {name:<20} {type_:<15} {notnull:<8} {str(default):<15} {pk:<8}")
        
        # 2. 打印数据总数
        print("\n" + "=" * 80)
        cursor.execute("SELECT COUNT(*) FROM history")
        count = cursor.fetchone()[0]
        print(f"\n【数据总数】: {count} 条记录")
        
        # 3. 打印所有数据
        if count > 0:
            print("\n【所有数据】")
            print("-" * 80)
            cursor.execute("SELECT * FROM history")
            rows = cursor.fetchall()
            
            # 获取列名
            column_names = [description[0] for description in cursor.description]
            
            # 打印列名
            header = " | ".join([f"{name:<15}" for name in column_names])
            print(header)
            print("-" * len(header))
            
            # 打印每一行数据
            for row in rows:
                row_str = " | ".join([f"{str(val):<15}" for val in row])
                print(row_str)
        else:
            print("\n表中没有数据")
        
        print("\n" + "=" * 80)
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    
    finally:
        conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    check_sqlite_db()
