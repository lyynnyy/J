#!/bin/bash
# 生产环境启动脚本

# 检查数据库是否存在
if [ ! -f "demo.db" ]; then
    echo "数据库文件不存在，正在构建..."
    python3 db_build.py
fi

# 检查是否安装了 gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "正在安装 gunicorn..."
    pip install gunicorn
fi

# 启动应用
echo "正在启动应用..."
gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} web_app:app
