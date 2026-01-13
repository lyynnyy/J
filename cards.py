#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡片定义模块 - 下钻卡定义
"""

# L0下钻卡定义
L0_DRILL_CARDS = [
    {
        'id': 'C1',
        'title': '旅程阶段断点下钻',
        'description': '查看 compare→decide、decide→purchase 的边转化/流失',
        'level': 'L1'
    },
    {
        'id': 'C2',
        'title': '渠道下钻',
        'description': '按渠道查看 decide→purchase 断点',
        'level': 'L1'
    },
    {
        'id': 'C3',
        'title': '购买决策细分下钻',
        'description': '分析"进入决策阶段但未购买"用户的无效浏览问题',
        'level': 'L2'
    }
]

# L1下钻卡定义（C1之后）
L1_DRILL_CARDS = [
    {
        'id': 'C3',
        'title': '购买决策细分下钻',
        'description': '分析"进入决策阶段但未购买"用户的两类问题：无效浏览过多、列表无点击',
        'level': 'L2'
    }
]

# L2下钻卡定义（C3之后）
L2_DRILL_CARDS = [
    {
        'id': 'C31',
        'title': '无效页面名称下钻',
        'description': '查看Top无效页面，用于UI调整/删除页面',
        'level': 'L3'
    },
    {
        'id': 'C32',
        'title': '未点击商品用户偏好下钻',
        'description': '分析"到达列表页但未点击商品"用户的历史购买偏好',
        'level': 'L3'
    }
]

def get_drill_card(card_id):
    """根据card_id获取下钻卡定义"""
    for card in L0_DRILL_CARDS:
        if card['id'] == card_id:
            return card
    for card in L1_DRILL_CARDS:
        if card['id'] == card_id:
            return card
    for card in L2_DRILL_CARDS:
        if card['id'] == card_id:
            return card
    return None
