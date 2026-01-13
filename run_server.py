#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 用于启动Flask应用
"""

import sys
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app import app
    
    print("=" * 50)
    print("启动分析型智能体 Web POC")
    print("=" * 50)
    print(f"模板目录: {app.template_folder}")
    print(f"静态文件目录: {app.static_folder}")
    print(f"访问地址: http://localhost:5000")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
