# Render 配置 Build Command 步骤

## 🎯 问题

Build Command 没有配置，导致数据库文件没有被构建，所以 `/api/ask` 路由报错。

## 🔧 解决步骤

### 步骤 1：进入 Settings

1. 在 Render Dashboard 中，点击你的服务名称
2. 点击顶部导航栏的 **"Settings"** 标签

### 步骤 2：找到 Build Command 配置

在 Settings 页面中，查找以下部分：
- **Build & Deploy** 部分
- 或 **Build Command** 字段
- 或滚动查找包含 "Build" 的配置项

### 步骤 3：填写 Build Command

在 **Build Command** 字段中，填写：

```
pip install -r requirements.txt && python db_build.py
```

### 步骤 4：同时配置 Start Command

确保 **Start Command** 配置为：

```
gunicorn --bind 0.0.0.0:$PORT web_app:app
```

### 步骤 5：保存配置

- 点击页面底部的 **"Save Changes"** 按钮
- Render 会自动重新部署

### 步骤 6：等待部署完成

- 查看 Logs，等待部署完成
- 应该能看到数据库构建的输出

---

## 📝 完整配置示例

由于你的代码在根目录，完整配置应该是：

```
Name: agent-poc（或你的服务名称）
Region: （你选择的区域）
Branch: main
Root Directory: （留空，因为代码在根目录）
Publish Directory: .
Build Command: pip install -r requirements.txt && python db_build.py
Start Command: gunicorn --bind 0.0.0.0:$PORT web_app:app
```

---

## 🔍 如果找不到 Build Command 字段

### 可能的情况：

1. **界面版本不同**
   - 尝试查找 "Commands"、"Build & Deploy" 或类似的选项
   - 或查找包含 "build" 关键词的字段

2. **服务类型不对**
   - 确认服务类型是 "Web Service"（不是 Static Site）
   - Static Site 不需要 Build Command

3. **权限问题**
   - 确认你是服务的所有者
   - 或联系服务创建者

---

## ✅ 配置后的验证

配置并重新部署后，在 Logs 中应该能看到：

```
==> Building...
==> Installing dependencies...
==> Building database...
数据验证:
  用户数: xxx
  旅程事件数: xxx
数据库构建完成: demo.db
==> Starting service...
[INFO] Booting worker...
[INFO] Listening at: http://0.0.0.0:xxxxx
```

---

## 🆘 如果还是找不到

请告诉我：
1. 在 Settings 页面，你能看到哪些配置字段？
2. 有没有看到 "Build"、"Command"、"Deploy" 等关键词？
3. 服务类型是什么？（Web Service 还是其他？）

有了这些信息，我可以给你更精确的指导！
