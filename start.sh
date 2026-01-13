#!/bin/bash
# 启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "清理端口 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null
sleep 1

echo "检查数据库..."
if [ ! -f "demo.db" ]; then
    echo "数据库不存在，正在创建..."
    python3 db_build.py
fi

echo "=========================================="
echo "启动 Flask 应用..."
echo "访问地址: http://127.0.0.1:5000"
echo "按 Ctrl+C 停止"
echo "=========================================="

python3 web_app.py
