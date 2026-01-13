# Render /api/ask 错误修复

## 🔍 错误分析

错误信息：`Exception on /api/ask [POST]`

**最可能的原因：数据库文件不存在或数据库表不存在**

`/api/ask` 路由会调用 `queries.get_l0()` 函数查询数据库，如果数据库文件不存在或表不存在，就会报错。

---

## 🎯 解决方案

### 步骤 1：查看完整的错误信息

在 Render Logs 中，找到完整的错误堆栈，应该会显示类似：

```
FileNotFoundError: [Errno 2] No such file or directory: 'demo.db'
```

或

```
sqlite3.OperationalError: no such table: journey_events
```

### 步骤 2：确保 Build Command 包含数据库构建

在 Render Settings 中，检查 **Build Command**，应该包含数据库构建：

```
pip install -r requirements.txt && python db_build.py
```

如果代码在子目录 `poc_demo` 中：

```
cd poc_demo && pip install -r requirements.txt && python db_build.py
```

### 步骤 3：检查数据库文件是否被 .gitignore 排除

数据库文件 `demo.db` 在 `.gitignore` 中，所以不会提交到 GitHub。

**解决方案：在 Build Command 中构建数据库**

确保 Build Command 包含 `python db_build.py`，这样每次部署时都会重新构建数据库。

---

## 🔧 修复步骤

### 1. 修改 Build Command

在 Render Settings 中：

**如果代码在根目录：**

```
Build Command: pip install -r requirements.txt && python db_build.py
```

**如果代码在子目录 `poc_demo`（Root Directory 设置为 `poc_demo`）：**

```
Build Command: pip install -r requirements.txt && python db_build.py
```

**如果代码在子目录但没有设置 Root Directory：**

```
Build Command: cd poc_demo && pip install -r requirements.txt && python db_build.py
```

### 2. 保存并重新部署

- 点击 "Save Changes"
- Render 会自动重新部署
- 等待部署完成（查看 Logs 确认数据库构建成功）

### 3. 验证数据库构建

在 Render Logs 中，查找数据库构建的输出，应该看到：

```
数据验证:
  用户数: xxx
  旅程事件数: xxx
  ...
数据库构建完成: demo.db
```

---

## 🐛 常见错误和解决方法

### 错误 1：FileNotFoundError: demo.db

**原因**：数据库文件不存在

**解决**：确保 Build Command 包含 `python db_build.py`

### 错误 2：sqlite3.OperationalError: no such table

**原因**：数据库文件存在但表没有创建

**解决**：
1. 检查 `db_build.py` 是否正确执行
2. 查看 Logs 确认数据库构建过程没有错误

### 错误 3：数据库构建失败

**原因**：`data.sql` 文件不存在或路径错误

**解决**：
1. 确认 `data.sql` 文件在正确位置
2. 如果代码在子目录，检查 `db_build.py` 中的路径

---

## 📝 完整的推荐配置

### 配置 A：代码在根目录

```
Root Directory: （留空）
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
Publish Directory: .
```

### 配置 B：代码在子目录 `poc_demo`

```
Root Directory: poc_demo
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
Publish Directory: .
```

---

## ✅ 验证修复

修复后，测试以下端点：

1. **健康检查**：
   ```
   https://你的域名.onrender.com/api/health
   ```
   应该返回 JSON：`{"status": "ok", ...}`

2. **登录页面**：
   ```
   https://你的域名.onrender.com/login
   ```
   应该显示登录表单

3. **API 端点**（需要先登录）：
   ```
   POST https://你的域名.onrender.com/api/ask
   ```
   应该能正常返回数据

---

## 🔍 如果问题仍然存在

请提供完整的错误堆栈信息，包括：

1. 完整的错误信息（从 Logs 中复制）
2. Build Command 的配置
3. 代码在 GitHub 的位置（根目录还是子目录）

这样我可以更精确地帮你解决问题！
