#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理模块 - 保存当前"异常断点/异常阶段"等可复用参数
"""

import json
import os

STATE_FILE = 'state.json'

def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'anomaly_edge': 'decide→purchase',
        'anomaly_stage': 'decide'
    }

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def reset_state():
    """重置状态"""
    default_state = {
        'anomaly_edge': 'decide→purchase',
        'anomaly_stage': 'decide'
    }
    save_state(default_state)
    return default_state

def update_state(**kwargs):
    """更新状态"""
    state = load_state()
    state.update(kwargs)
    save_state(state)
    return state
