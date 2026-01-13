# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制应用代码
COPY . .

# 构建数据库（重要：在容器启动前构建数据库）
RUN python3 db_build.py

# 暴露端口
EXPOSE 5000

# 使用 gunicorn 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web_app:app"]
