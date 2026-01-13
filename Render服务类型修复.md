# Render 服务类型修复

## 🔍 问题诊断

如果在 Settings 中找不到 Build Command 和 Start Command，**最可能的原因是创建了错误的服务类型**。

### 检查服务类型

1. 在 Render Dashboard 中，点击你的服务
2. 查看服务详情页顶部或 Overview 标签
3. 确认服务类型显示的是什么：
   - **Web Service** ✅（正确，应该有 Build/Start Command）
   - **Static Site** ❌（错误，只用于静态文件）
   - **Background Worker** ❌（错误，用于后台任务）

---

## 🎯 解决方案

### 如果服务类型是 Static Site

**需要删除并重新创建为 Web Service：**

#### 步骤 1：删除当前服务

1. 进入服务详情页
2. 点击 "Settings" 标签
3. 滚动到页面最底部
4. 找到 "Danger Zone" 或 "Delete Service" 部分
5. 点击 "Delete Service"
6. 确认删除

#### 步骤 2：重新创建 Web Service

1. 在 Render Dashboard，点击 **"New +"** 按钮
2. **重要**：选择 **"Web Service"**（不是 Static Site）
3. 连接 GitHub 仓库：选择 `lyynnyy/J`
4. 填写配置：

```
Name: agent-poc
Region: （选择区域）
Branch: main
Root Directory: （留空，因为代码在根目录）
Publish Directory: .
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
```

5. 点击 "Create Web Service"

---

## 📝 创建 Web Service 时的完整配置

### 基本信息

- **Name**: `agent-poc`（或任意名称）
- **Region**: 选择区域（如 Singapore）
- **Branch**: `main`
- **Root Directory**: （留空，因为代码在根目录）

### 构建和启动

- **Build Command**: 
  ```
  pip install -r requirements.txt && python db_build.py
  ```
  
- **Start Command**: 
  ```
  gunicorn --bind 0.0.0.0:$PORT web_app:app
  ```

- **Publish Directory**: `.`

### 环境变量（可选）

- **SECRET_KEY**: （可选，用于 session 加密）
- **PASSWORD**: （可选，如果不设置则使用默认值）

---

## 🔍 如果确认是 Web Service 但找不到配置

### 可能的原因：

1. **界面版本不同**
   - 尝试查找 "Commands"、"Build & Deploy"、"Deploy" 等标签
   - 或在创建服务时填写（而不是在 Settings 中）

2. **配置在创建时填写**
   - 删除当前服务
   - 重新创建时，在创建表单中填写 Build Command 和 Start Command

3. **使用 Render CLI**
   - 如果网页界面找不到，可以使用 Render CLI 配置

---

## ✅ 验证

创建 Web Service 后，应该能看到：

1. **在服务详情页**：
   - Overview 标签显示服务类型为 "Web Service"
   - Logs 标签可以看到构建和启动日志

2. **在 Settings 页面**：
   - 能看到 Build Command 和 Start Command 配置
   - 可以修改这些配置

3. **部署成功后**：
   - 访问 URL 应该能正常显示登录页面
   - `/api/ask` 应该能正常工作

---

## 🆘 如果还是不行

请告诉我：

1. **服务类型是什么？**
   - 在服务详情页查看，是 "Web Service"、"Static Site" 还是其他？

2. **在创建服务时，你选择了什么类型？**
   - 是 "Web Service" 还是 "Static Site"？

3. **在 Settings 页面，你能看到哪些配置项？**
   - 列出所有可见的配置字段名称

有了这些信息，我可以给你更精确的指导！
