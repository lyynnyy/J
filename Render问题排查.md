# Render "Not Found" 错误排查指南

## 🔍 第一步：查看 Render 日志

1. 在 Render Dashboard 中，点击你的服务
2. 点击 "Logs" 标签
3. 查看最新的日志，寻找错误信息

常见错误信息：
- `ModuleNotFoundError: No module named 'web_app'` - 模块找不到
- `FileNotFoundError: [Errno 2] No such file or directory: 'demo.db'` - 数据库文件不存在
- `OSError: [Errno 98] Address already in use` - 端口问题

---

## 🎯 可能的原因和解决方案

### 问题 1：代码在子目录中，路径配置错误

**如果你的代码在 GitHub 仓库的 `poc_demo` 子目录中：**

#### 检查方法：
查看 GitHub 仓库结构，确认代码位置：
- 如果代码在根目录：`/web_app.py`
- 如果代码在子目录：`/poc_demo/web_app.py`

#### 解决方案 A：代码在子目录 `poc_demo` 中

在 Render 配置中：

```
Root Directory: poc_demo
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn web_app:app
Publish Directory: .
```

#### 解决方案 B：代码在根目录中

在 Render 配置中：

```
Root Directory: （留空）
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn web_app:app
Publish Directory: .
```

---

### 问题 2：Start Command 路径不正确

如果代码在子目录中，可能需要指定完整路径：

**尝试修改 Start Command 为：**

```
cd poc_demo && gunicorn web_app:app
```

或者（如果 Root Directory 已设置为 `poc_demo`）：

```
gunicorn web_app:app
```

---

### 问题 3：数据库文件不存在

**检查 Build Command 是否包含数据库构建：**

确保 Build Command 包含：
```
pip install -r requirements.txt && python db_build.py
```

如果代码在子目录，应该是：
```
cd poc_demo && pip install -r requirements.txt && python db_build.py
```

---

### 问题 4：gunicorn 找不到应用模块

**尝试修改 Start Command：**

如果代码在根目录：
```
gunicorn --chdir poc_demo web_app:app
```

或者使用 Python 模块方式：
```
python -m gunicorn web_app:app
```

---

### 问题 5：端口绑定问题

Render 会自动设置 PORT 环境变量，但 gunicorn 需要正确绑定。

**修改 Start Command 为：**

```
gunicorn web_app:app --bind 0.0.0.0:$PORT
```

或者：
```
gunicorn --bind 0.0.0.0:$PORT web_app:app
```

---

## 🔧 推荐的完整配置

### 配置方案 A：代码在根目录

```
Name: agent-poc
Region: （选择区域）
Branch: main
Root Directory: （留空）
Publish Directory: .
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
```

### 配置方案 B：代码在子目录 `poc_demo`

```
Name: agent-poc
Region: （选择区域）
Branch: main
Root Directory: poc_demo
Publish Directory: .
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
```

---

## 🐛 调试步骤

### 1. 检查应用是否启动

在 Render Logs 中查找：
- ✅ `Booting worker` - 表示 gunicorn 启动成功
- ✅ `Listening at: http://0.0.0.0:xxxx` - 表示应用正在监听
- ❌ `ModuleNotFoundError` - 模块找不到
- ❌ `FileNotFoundError` - 文件找不到

### 2. 测试健康检查端点

如果应用启动成功，尝试访问：
```
https://你的域名.onrender.com/api/health
```

如果返回 JSON，说明应用运行正常，可能是路由问题。

### 3. 检查路由

确保访问的是正确的 URL：
- 首页：`https://你的域名.onrender.com/`
- 登录页：`https://你的域名.onrender.com/login`

### 4. 查看完整错误信息

在 Render Logs 中，查看完整的错误堆栈，找到具体的错误原因。

---

## 💡 快速修复尝试

### 尝试 1：修改 Start Command

将 Start Command 改为：
```
gunicorn --bind 0.0.0.0:$PORT --chdir poc_demo web_app:app
```

（如果代码在子目录，将 `poc_demo` 改为你的子目录名）

### 尝试 2：使用 Python 直接运行（测试用）

临时修改 Start Command 为：
```
python web_app.py
```

（仅用于测试，生产环境应使用 gunicorn）

### 尝试 3：检查文件结构

在 Build Command 中添加调试信息：
```
pip install -r requirements.txt && python db_build.py && ls -la
```

查看构建后的文件列表，确认所有文件都在。

---

## 📞 需要帮助？

如果以上方法都不行，请提供：
1. Render Logs 的完整错误信息
2. 你的 GitHub 仓库结构（代码在根目录还是子目录）
3. 当前的 Render 配置（Build Command 和 Start Command）
