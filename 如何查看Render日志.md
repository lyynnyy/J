# 如何查看 Render 日志

## 📍 查找日志的步骤

### 方法 1：在 Dashboard 中查看（推荐）

1. **登录 Render**
   - 访问 https://dashboard.render.com
   - 登录你的账号

2. **找到你的服务**
   - 在 Dashboard 主页，找到你创建的服务（如 `agent-poc`）
   - 点击服务名称进入详情页

3. **查看日志**
   - 在服务详情页，顶部有几个标签：
     - **Overview**（概览）
     - **Logs**（日志）← 点击这个
     - **Metrics**（指标）
     - **Settings**（设置）
   - 点击 **"Logs"** 标签

4. **查看日志内容**
   - 日志会实时显示
   - 可以滚动查看历史日志
   - 最新的日志在底部

### 方法 2：如果找不到服务

1. **检查服务状态**
   - 在 Dashboard 主页，查看服务列表
   - 确认服务是否显示为 "Live"（运行中）或 "Build failed"（构建失败）

2. **如果服务不存在**
   - 可能部署失败了
   - 检查是否有错误提示
   - 重新创建服务

### 方法 3：通过 URL 直接访问

如果你知道服务的 URL，可以：
1. 访问：`https://dashboard.render.com`
2. 在服务列表中查找
3. 或使用浏览器搜索功能（Ctrl+F / Cmd+F）搜索服务名称

---

## 🔍 日志中应该看到什么

### 正常的日志应该显示：

```
==> Building...
==> Downloading code...
==> Installing dependencies...
==> Building database...
==> Starting service...
[INFO] Booting worker with pid: xxx
[INFO] Listening at: http://0.0.0.0:xxxxx
```

### 错误的日志可能显示：

```
ModuleNotFoundError: No module named 'web_app'
FileNotFoundError: [Errno 2] No such file or directory: 'demo.db'
ERROR: Could not open requirements file
```

---

## 📸 截图位置参考

如果你使用网页版 Render：

```
Dashboard 主页
  └── 你的服务卡片（agent-poc）
       └── 点击进入
            └── 顶部标签栏
                 ├── Overview
                 ├── Logs ← 点击这里
                 ├── Metrics
                 └── Settings
```

---

## 🆘 如果还是找不到

### 替代方案：检查服务状态

即使看不到详细日志，也可以：

1. **查看服务状态**
   - 在 Dashboard 主页，查看服务卡片
   - 状态显示：
     - ✅ **Live** - 服务运行中
     - ⚠️ **Build failed** - 构建失败
     - ⚠️ **Deploy failed** - 部署失败
     - ⏸️ **Suspended** - 已暂停

2. **测试访问**
   - 点击服务卡片上的 URL
   - 或访问 Render 提供的域名
   - 看是否能访问

3. **重新部署**
   - 在服务详情页，点击 "Manual Deploy"
   - 或修改配置后自动重新部署

---

## 💡 快速诊断

即使看不到日志，也可以尝试：

### 1. 检查服务 URL

访问 Render 提供的 URL（类似 `https://agent-poc.onrender.com`）：
- 如果显示 "Not Found" → 应用可能没启动或路由问题
- 如果显示其他错误 → 根据错误信息判断
- 如果完全无法访问 → 服务可能未启动

### 2. 测试健康检查端点

访问：`https://你的域名.onrender.com/api/health`

- 如果返回 JSON → 应用运行正常，可能是路由问题
- 如果 404 → 应用可能没启动或路由配置错误
- 如果 401 → 应用运行正常，需要登录

### 3. 尝试访问登录页

访问：`https://你的域名.onrender.com/login`

- 如果显示登录页面 → 应用运行正常！
- 如果 404 → 路由或应用启动问题

---

## 🎯 下一步

请告诉我：

1. **你能访问服务吗？**
   - 访问 Render 提供的 URL，看到了什么？

2. **服务状态是什么？**
   - 在 Dashboard 中，服务显示为什么状态？（Live / Build failed / Deploy failed）

3. **访问 URL 时看到什么？**
   - 完全无法访问？
   - 显示 "Not Found"？
   - 显示其他错误信息？

有了这些信息，我可以帮你进一步诊断问题！
