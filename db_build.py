#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库构建脚本
创建SQLite数据库和表结构，导入示例数据
"""

import sqlite3
import os

DB_FILE = 'demo.db'

def create_tables(cursor):
    """创建数据表"""
    # users表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        first_channel TEXT,
        user_type TEXT,
        created_at TEXT
    )
    ''')
    
    # journey_events表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journey_events (
        je_id TEXT PRIMARY KEY,
        user_id TEXT,
        ts TEXT,
        journey_id TEXT,
        step TEXT,
        step_name TEXT,
        order_id TEXT,
        amount REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # decision_events表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS decision_events (
        de_id TEXT PRIMARY KEY,
        user_id TEXT,
        ts TEXT,
        journey_id TEXT,
        session_id TEXT,
        page_name TEXT,
        page_type TEXT,
        action TEXT,
        button_id TEXT,
        is_key_page INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # items表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        item_id TEXT PRIMARY KEY,
        item_name TEXT,
        category_name TEXT,
        tag TEXT
    )
    ''')
    
    # item_events表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_events (
        ie_id TEXT PRIMARY KEY,
        user_id TEXT,
        ts TEXT,
        journey_id TEXT,
        session_id TEXT,
        page_name TEXT,
        event_name TEXT,
        item_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (item_id) REFERENCES items(item_id)
    )
    ''')
    
    # order_items表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        oi_id TEXT PRIMARY KEY,
        order_id TEXT,
        user_id TEXT,
        item_id TEXT,
        qty INTEGER,
        amount REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (item_id) REFERENCES items(item_id)
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_events_user_ts ON item_events(user_id, ts)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_user ON order_items(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision_events_user_ts ON decision_events(user_id, ts)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_journey_events_user_ts ON journey_events(user_id, ts)')
    
    print("数据表创建成功")

def load_data(cursor):
    """从data.sql加载数据"""
    sql_file = os.path.join(os.path.dirname(__file__), 'data.sql')
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 执行SQL文件内容
    try:
        cursor.executescript(sql_content)
        print("数据导入成功")
    except sqlite3.Error as e:
        print(f"执行SQL时出错: {e}")
        raise

def main():
    """主函数"""
    # 删除旧数据库（如果存在）
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"删除旧数据库: {DB_FILE}")
    
    # 创建数据库连接
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 创建表
        create_tables(cursor)
        
        # 加载数据
        load_data(cursor)
        
        # 提交事务
        conn.commit()
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM journey_events")
        je_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM decision_events")
        de_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM items")
        items_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM item_events")
        ie_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM order_items")
        oi_count = cursor.fetchone()[0]
        
        print(f"\n数据验证:")
        print(f"  用户数: {user_count}")
        print(f"  旅程事件数: {je_count}")
        print(f"  决策事件数: {de_count}")
        print(f"  商品数: {items_count}")
        print(f"  商品事件数: {ie_count}")
        print(f"  订单商品数: {oi_count}")
        print(f"\n数据库构建完成: {DB_FILE}")
        
    except Exception as e:
        conn.rollback()
        print(f"错误: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
