#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则模块 - 用于锁定"最大断点边"等规则
"""

# 默认最大断点边
DEFAULT_ANOMALY_EDGE = 'decide→purchase'

def get_anomaly_edge():
    """获取当前锁定的异常边"""
    # 可以扩展为从state读取
    return DEFAULT_ANOMALY_EDGE
