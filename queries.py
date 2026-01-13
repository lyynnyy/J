#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询模块 - 所有SQL查询函数
"""

import sqlite3
from datetime import datetime

DB_FILE = 'demo.db'

# 时间窗定义
PREV_7D_START = '2026-01-01'
PREV_7D_END = '2026-01-07'
CURR_7D_START = '2026-01-08'
CURR_7D_END = '2026-01-14'

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_FILE)

def get_l0():
    """
    L0查询：总体转化对比（curr_7d vs prev_7d）
    返回：compare→purchase的转化率对比
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # prev_7d: compare→purchase转化率
        cursor.execute('''
        SELECT 
            COUNT(DISTINCT CASE WHEN step = 'compare' THEN user_id END) as compare_users,
            COUNT(DISTINCT CASE WHEN step = 'purchase' THEN user_id END) as purchase_users
        FROM journey_events
        WHERE ts >= ? AND ts <= ?
        ''', (PREV_7D_START, PREV_7D_END))
        
        prev_row = cursor.fetchone()
        prev_compare = prev_row[0] or 0
        prev_purchase = prev_row[1] or 0
        prev_rate = (prev_purchase / prev_compare * 100) if prev_compare > 0 else 0
        
        # curr_7d: compare→purchase转化率
        cursor.execute('''
        SELECT 
            COUNT(DISTINCT CASE WHEN step = 'compare' THEN user_id END) as compare_users,
            COUNT(DISTINCT CASE WHEN step = 'purchase' THEN user_id END) as purchase_users
        FROM journey_events
        WHERE ts >= ? AND ts <= ?
        ''', (CURR_7D_START, CURR_7D_END))
        
        curr_row = cursor.fetchone()
        curr_compare = curr_row[0] or 0
        curr_purchase = curr_row[1] or 0
        curr_rate = (curr_purchase / curr_compare * 100) if curr_compare > 0 else 0
        
        return {
            'prev_7d': {
                'compare_users': prev_compare,
                'purchase_users': prev_purchase,
                'rate': prev_rate
            },
            'curr_7d': {
                'compare_users': curr_compare,
                'purchase_users': curr_purchase,
                'rate': curr_rate
            },
            'change': curr_rate - prev_rate
        }
    finally:
        conn.close()

def get_l1_stage_drop():
    """
    L1查询：旅程阶段断点下钻
    返回：compare→decide、decide→purchase的边转化/流失
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # curr_7d: 各边的转化情况
        # compare→decide
        cursor.execute('''
        SELECT COUNT(DISTINCT user_id)
        FROM journey_events
        WHERE ts >= ? AND ts <= ? AND step = 'compare'
        ''', (CURR_7D_START, CURR_7D_END))
        compare_users = cursor.fetchone()[0] or 0
        
        cursor.execute('''
        SELECT COUNT(DISTINCT je1.user_id)
        FROM journey_events je1
        JOIN journey_events je2 ON je1.user_id = je2.user_id AND je1.journey_id = je2.journey_id
        WHERE je1.step = 'compare' AND je2.step = 'decide'
        AND je1.ts >= ? AND je1.ts <= ?
        AND je2.ts > je1.ts
        ''', (CURR_7D_START, CURR_7D_END))
        compare_to_decide = cursor.fetchone()[0] or 0
        
        # decide→purchase
        cursor.execute('''
        SELECT COUNT(DISTINCT user_id)
        FROM journey_events
        WHERE ts >= ? AND ts <= ? AND step = 'decide'
        ''', (CURR_7D_START, CURR_7D_END))
        decide_users = cursor.fetchone()[0] or 0
        
        cursor.execute('''
        SELECT COUNT(DISTINCT je1.user_id)
        FROM journey_events je1
        JOIN journey_events je2 ON je1.user_id = je2.user_id AND je1.journey_id = je2.journey_id
        WHERE je1.step = 'decide' AND je2.step = 'purchase'
        AND je1.ts >= ? AND je1.ts <= ?
        AND je2.ts > je1.ts
        ''', (CURR_7D_START, CURR_7D_END))
        decide_to_purchase = cursor.fetchone()[0] or 0
        
        compare_to_decide_rate = (compare_to_decide / compare_users * 100) if compare_users > 0 else 0
        decide_to_purchase_rate = (decide_to_purchase / decide_users * 100) if decide_users > 0 else 0
        
        return {
            'compare_to_decide': {
                'from_count': compare_users,
                'to_count': compare_to_decide,
                'rate': compare_to_decide_rate,
                'drop_count': compare_users - compare_to_decide
            },
            'decide_to_purchase': {
                'from_count': decide_users,
                'to_count': decide_to_purchase,
                'rate': decide_to_purchase_rate,
                'drop_count': decide_users - decide_to_purchase
            }
        }
    finally:
        conn.close()

def get_l2_channel_drill():
    """
    L2渠道下钻（可选）：按渠道看decide→purchase断点
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT 
            u.first_channel,
            COUNT(DISTINCT CASE WHEN je.step = 'decide' THEN je.user_id END) as decide_users,
            COUNT(DISTINCT CASE WHEN je.step = 'purchase' THEN je.user_id END) as purchase_users
        FROM users u
        LEFT JOIN journey_events je ON u.user_id = je.user_id
        WHERE je.ts >= ? AND je.ts <= ?
        GROUP BY u.first_channel
        ORDER BY decide_users DESC
        ''', (CURR_7D_START, CURR_7D_END))
        
        results = []
        for row in cursor.fetchall():
            channel, decide_count, purchase_count = row
            decide_count = decide_count or 0
            purchase_count = purchase_count or 0
            rate = (purchase_count / decide_count * 100) if decide_count > 0 else 0
            results.append({
                'channel': channel,
                'decide_users': decide_count,
                'purchase_users': purchase_count,
                'rate': rate,
                'drop_count': decide_count - purchase_count
            })
        
        return results
    finally:
        conn.close()

def get_l2_decision_invalid():
    """
    L2购买决策细分下钻：分析进入决策阶段但未购买的用户
    返回：
    1) 无效浏览次数分布
    2) 到达关键页(category)的比例
    3) 典型无效页面/按钮Top
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 找出curr_7d中进入decide但未purchase的用户
        cursor.execute('''
        SELECT DISTINCT je.user_id
        FROM journey_events je
        WHERE je.step = 'decide'
        AND je.ts >= ? AND je.ts <= ?
        AND je.user_id NOT IN (
            SELECT DISTINCT user_id
            FROM journey_events
            WHERE step = 'purchase' AND ts >= ? AND ts <= ?
        )
        ''', (CURR_7D_START, CURR_7D_END, CURR_7D_START, CURR_7D_END))
        
        lost_users = [row[0] for row in cursor.fetchall()]
        
        if not lost_users:
            return {
                'user_count': 0,
                'invalid_view_stats': {},
                'key_page_reach_rate': 0,
                'top_invalid_pages': [],
                'top_invalid_buttons': []
            }
        
        user_placeholders = ','.join(['?'] * len(lost_users))
        
        # 1. 无效浏览次数统计（每个用户的无效浏览数）
        cursor.execute(f'''
        SELECT user_id, COUNT(*) as invalid_count
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        GROUP BY user_id
        ''', lost_users + [CURR_7D_START, CURR_7D_END])
        
        invalid_counts = [row[1] for row in cursor.fetchall()]
        
        # 计算统计值
        avg_invalid = sum(invalid_counts) / len(invalid_counts) if invalid_counts else 0
        sorted_counts = sorted(invalid_counts)
        median_invalid = sorted_counts[len(sorted_counts) // 2] if sorted_counts else 0
        
        # 2. 关键页到达率（category或is_key_page=1）
        cursor.execute(f'''
        SELECT COUNT(DISTINCT user_id)
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND (page_name = 'category' OR is_key_page = 1)
        ''', lost_users + [CURR_7D_START, CURR_7D_END])
        
        reached_key_page_count = cursor.fetchone()[0] or 0
        key_page_reach_rate = (reached_key_page_count / len(lost_users) * 100) if lost_users else 0
        
        # 3. Top无效页面
        cursor.execute(f'''
        SELECT page_name, COUNT(*) as count
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND page_name IS NOT NULL
        GROUP BY page_name
        ORDER BY count DESC
        LIMIT 10
        ''', lost_users + [CURR_7D_START, CURR_7D_END])
        
        top_invalid_pages = [{'page': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # 4. Top无效按钮
        cursor.execute(f'''
        SELECT button_id, COUNT(*) as count
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND button_id IS NOT NULL
        GROUP BY button_id
        ORDER BY count DESC
        LIMIT 10
        ''', lost_users + [CURR_7D_START, CURR_7D_END])
        
        top_invalid_buttons = [{'button': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        return {
            'user_count': len(lost_users),
            'invalid_view_stats': {
                'avg': round(avg_invalid, 2),
                'median': median_invalid,
                'total': sum(invalid_counts),
                'distribution': {
                    'min': min(invalid_counts) if invalid_counts else 0,
                    'max': max(invalid_counts) if invalid_counts else 0
                }
            },
            'key_page_reach_rate': round(key_page_reach_rate, 2),
            'top_invalid_pages': top_invalid_pages,
            'top_invalid_buttons': top_invalid_buttons
        }
    finally:
        conn.close()

def get_l2_decision_diagnosis_v2(conn=None, period="curr_7d"):
    """
    L2购买决策细分下钻（v2）：同时识别两类问题
    人群：curr_7d 进入 decide(step=2) 且未 purchase(step=3)
    输出 evidence（两类问题）：
    - 问题 A：无效页面浏览过多
    - 问题 B：列表无点击（到达category但未点击商品）
    """
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    cursor = conn.cursor()
    
    try:
        period_start = CURR_7D_START if period == "curr_7d" else PREV_7D_START
        period_end = CURR_7D_END if period == "curr_7d" else PREV_7D_END
        
        # 找出curr_7d中进入decide但未purchase的用户
        cursor.execute('''
        SELECT DISTINCT je.user_id
        FROM journey_events je
        WHERE je.step = 'decide'
        AND je.ts >= ? AND je.ts <= ?
        AND je.user_id NOT IN (
            SELECT DISTINCT user_id
            FROM journey_events
            WHERE step = 'purchase' AND ts >= ? AND ts <= ?
        )
        ''', (period_start, period_end, period_start, period_end))
        
        lost_users = [row[0] for row in cursor.fetchall()]
        
        if not lost_users:
            return {
                'user_count': 0,
                'invalid_view_avg': 0,
                'top_invalid_pages': [],
                'key_page_reach_users': 0,
                'no_item_click_users': 0,
                'no_item_click_rate': 0,
                'impression_items_avg': 0
            }
        
        user_placeholders = ','.join(['?'] * len(lost_users))
        
        # 问题 A：无效页面浏览统计
        cursor.execute(f'''
        SELECT user_id, COUNT(*) as invalid_count
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        GROUP BY user_id
        ''', lost_users + [period_start, period_end])
        
        invalid_counts = [row[1] for row in cursor.fetchall()]
        invalid_view_avg = sum(invalid_counts) / len(invalid_counts) if invalid_counts else 0
        
        # Top无效页面（前5个）
        cursor.execute(f'''
        SELECT page_name, COUNT(*) as count, COUNT(DISTINCT user_id) as users
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND page_name IS NOT NULL
        GROUP BY page_name
        ORDER BY count DESC
        LIMIT 5
        ''', lost_users + [period_start, period_end])
        
        top_invalid_pages = [{'page_name': row[0], 'events': row[1], 'users': row[2]} for row in cursor.fetchall()]
        
        # 问题 B：列表无点击统计
        # 1. 到达category的用户数
        cursor.execute(f'''
        SELECT COUNT(DISTINCT user_id)
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND (page_name = 'category' OR is_key_page = 1)
        ''', lost_users + [period_start, period_end])
        
        key_page_reach_users = cursor.fetchone()[0] or 0
        
        # 2. 到达category但未点击商品的用户数
        cursor.execute(f'''
        SELECT DISTINCT de.user_id
        FROM decision_events de
        WHERE de.user_id IN ({user_placeholders})
        AND de.ts >= ? AND de.ts <= ?
        AND (de.page_name = 'category' OR de.is_key_page = 1)
        AND de.user_id NOT IN (
            SELECT DISTINCT ie.user_id
            FROM item_events ie
            WHERE ie.event_name = 'item_click'
            AND ie.ts >= ? AND ie.ts <= ?
        )
        ''', lost_users + [period_start, period_end, period_start, period_end])
        
        no_item_click_users = len(cursor.fetchall())
        no_item_click_rate = (no_item_click_users / key_page_reach_users * 100) if key_page_reach_users > 0 else 0
        
        # 3. 平均曝光商品数（可选）
        cursor.execute(f'''
        SELECT de.user_id, COUNT(DISTINCT ie.item_id) as item_count
        FROM decision_events de
        LEFT JOIN item_events ie ON de.user_id = ie.user_id 
            AND de.journey_id = ie.journey_id
            AND ie.page_name = 'category'
            AND ie.event_name = 'item_impression'
            AND ie.ts >= ? AND ie.ts <= ?
        WHERE de.user_id IN ({user_placeholders})
        AND de.ts >= ? AND de.ts <= ?
        AND (de.page_name = 'category' OR de.is_key_page = 1)
        GROUP BY de.user_id
        ''', [period_start, period_end] + lost_users + [period_start, period_end])
        
        impression_counts = [row[1] for row in cursor.fetchall()]
        impression_items_avg = sum(impression_counts) / len(impression_counts) if impression_counts else 0
        
        return {
            'user_count': len(lost_users),
            'invalid_view_avg': round(invalid_view_avg, 2),
            'top_invalid_pages': top_invalid_pages,
            'key_page_reach_users': key_page_reach_users,
            'no_item_click_users': no_item_click_users,
            'no_item_click_rate': round(no_item_click_rate, 2),
            'impression_items_avg': round(impression_items_avg, 2)
        }
    finally:
        if should_close:
            conn.close()

def get_l3_invalid_pages(conn=None, period="curr_7d", top_n=10):
    """
    L3无效页面名称下钻
    输出 top_invalid_pages（page_name + users/events）
    """
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    cursor = conn.cursor()
    
    try:
        period_start = CURR_7D_START if period == "curr_7d" else PREV_7D_START
        period_end = CURR_7D_END if period == "curr_7d" else PREV_7D_END
        
        # 找出curr_7d中进入decide但未purchase的用户
        cursor.execute('''
        SELECT DISTINCT je.user_id
        FROM journey_events je
        WHERE je.step = 'decide'
        AND je.ts >= ? AND je.ts <= ?
        AND je.user_id NOT IN (
            SELECT DISTINCT user_id
            FROM journey_events
            WHERE step = 'purchase' AND ts >= ? AND ts <= ?
        )
        ''', (period_start, period_end, period_start, period_end))
        
        lost_users = [row[0] for row in cursor.fetchall()]
        
        if not lost_users:
            return {'top_invalid_pages': []}
        
        user_placeholders = ','.join(['?'] * len(lost_users))
        
        # Top无效页面
        cursor.execute(f'''
        SELECT page_name, COUNT(*) as events, COUNT(DISTINCT user_id) as users
        FROM decision_events
        WHERE user_id IN ({user_placeholders})
        AND ts >= ? AND ts <= ?
        AND page_name IS NOT NULL
        GROUP BY page_name
        ORDER BY events DESC
        LIMIT ?
        ''', lost_users + [period_start, period_end, top_n])
        
        top_invalid_pages = [
            {'page_name': row[0], 'events': row[1], 'users': row[2]} 
            for row in cursor.fetchall()
        ]
        
        return {'top_invalid_pages': top_invalid_pages}
    finally:
        if should_close:
            conn.close()

def get_l3_no_click_preference(conn=None, period="curr_7d", top_n=5):
    """
    L3未点击商品用户偏好下钻
    圈人群条件（必须严格）：
    - curr_7d 进入 decide
    - 未 purchase
    - 到达 category
    - item_click = 0
    输出：
    - audience_size
    - historical_top_items（join order_items + items）
    - historical_top_categories
    - audience_filters（结构化条件）
    """
    if conn is None:
        conn = get_db_connection()
        should_close = True
    else:
        should_close = False
    
    cursor = conn.cursor()
    
    try:
        period_start = CURR_7D_START if period == "curr_7d" else PREV_7D_START
        period_end = CURR_7D_END if period == "curr_7d" else PREV_7D_END
        
        # 圈出严格人群：进入decide、未purchase、到达category、无item_click
        cursor.execute('''
        SELECT DISTINCT de.user_id
        FROM decision_events de
        INNER JOIN journey_events je ON de.user_id = je.user_id
        WHERE je.step = 'decide'
        AND je.ts >= ? AND je.ts <= ?
        AND de.user_id NOT IN (
            SELECT DISTINCT user_id
            FROM journey_events
            WHERE step = 'purchase' AND ts >= ? AND ts <= ?
        )
        AND (de.page_name = 'category' OR de.is_key_page = 1)
        AND de.ts >= ? AND de.ts <= ?
        AND de.user_id NOT IN (
            SELECT DISTINCT user_id
            FROM item_events
            WHERE event_name = 'item_click'
            AND ts >= ? AND ts <= ?
        )
        ''', (period_start, period_end, period_start, period_end, period_start, period_end, period_start, period_end))
        
        audience_users = [row[0] for row in cursor.fetchall()]
        audience_size = len(audience_users)
        
        if not audience_users:
            return {
                'audience_size': 0,
                'historical_top_items': [],
                'historical_top_categories': [],
                'audience_filters': {}
            }
        
        user_placeholders = ','.join(['?'] * len(audience_users))
        
        # 历史购买Top商品
        cursor.execute(f'''
        SELECT i.item_id, i.item_name, i.category_name, 
               COUNT(DISTINCT oi.user_id) as buyer_count,
               SUM(oi.qty) as total_qty,
               SUM(oi.amount) as total_amount
        FROM order_items oi
        INNER JOIN items i ON oi.item_id = i.item_id
        WHERE oi.user_id IN ({user_placeholders})
        GROUP BY i.item_id, i.item_name, i.category_name
        ORDER BY buyer_count DESC, total_qty DESC
        LIMIT ?
        ''', audience_users + [top_n])
        
        historical_top_items = [
            {
                'item_id': row[0],
                'item_name': row[1],
                'category_name': row[2],
                'buyer_count': row[3],
                'total_qty': row[4],
                'total_amount': round(row[5], 2)
            }
            for row in cursor.fetchall()
        ]
        
        # 历史购买Top类目
        cursor.execute(f'''
        SELECT i.category_name,
               COUNT(DISTINCT oi.user_id) as buyer_count,
               COUNT(DISTINCT oi.item_id) as item_count,
               SUM(oi.qty) as total_qty
        FROM order_items oi
        INNER JOIN items i ON oi.item_id = i.item_id
        WHERE oi.user_id IN ({user_placeholders})
        GROUP BY i.category_name
        ORDER BY buyer_count DESC, total_qty DESC
        LIMIT ?
        ''', audience_users + [top_n])
        
        historical_top_categories = [
            {
                'category_name': row[0],
                'buyer_count': row[1],
                'item_count': row[2],
                'total_qty': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # 人群筛选条件（结构化）
        audience_filters = {
            'period': period,
            'journey_id': 'J_BUY',
            'in_decide': 1,
            'no_purchase': 1,
            'reached_category': 1,
            'item_click': 0
        }
        
        return {
            'audience_size': audience_size,
            'historical_top_items': historical_top_items,
            'historical_top_categories': historical_top_categories,
            'audience_filters': audience_filters
        }
    finally:
        if should_close:
            conn.close()
