# Render 部署指南

本指南将帮助你在 Render 平台连接 GitHub 仓库并部署 Flask 应用。

---

## 📋 前提条件

1. ✅ **GitHub 仓库已准备好**
   - 你的仓库地址：https://github.com/lyynnyy/J
   - 代码已推送到 GitHub

2. ✅ **Render 账号**
   - 如果没有，访问 https://render.com 注册（可用 GitHub 账号快速注册）

---

## 🚀 部署步骤

### 步骤 1：登录 Render

1. 访问 https://render.com
2. 点击右上角 "Sign Up" 或 "Log In"
3. 推荐使用 "Continue with GitHub"（这样会自动授权，更方便）

### 步骤 2：创建 Web Service

1. 登录后，点击 Dashboard 左上角的 **"New +"** 按钮
2. 选择 **"Web Service"**

### 步骤 3：连接 GitHub 仓库

1. **选择连接方式**：
   - 如果使用 GitHub 登录，会看到你的仓库列表
   - 如果手动连接，点击 "Connect account" 授权 GitHub 访问

2. **选择仓库**：
   - 在仓库列表中，选择 `lyynnyy/J`（你的仓库）
   - 或搜索 "J" 找到你的仓库
   - 点击仓库名称

### 步骤 4：配置部署设置

填写以下信息：

#### 基本信息

- **Name**: `agent-poc`（或任意名称，用于标识这个服务）
- **Region**: 选择离你最近的区域（如 `Singapore` 或 `Oregon`）
- **Branch**: `main`（默认，确保代码在这个分支）
- **Root Directory**: 留空（如果代码在仓库根目录）或填写 `poc_demo`（如果代码在子目录）

⚠️ **注意**：如果你的代码在 `poc_demo` 子目录中，需要：
- 在 Root Directory 填写：`poc_demo`
- 或者在 GitHub 仓库中将代码移到根目录

#### 构建和启动命令

- **Runtime**: `Python 3`（Render 会自动检测）

- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
  
  如果你的代码在子目录：
  ```bash
  cd poc_demo && pip install -r requirements.txt
  ```

- **Start Command**:
  ```bash
  gunicorn web_app:app
  ```
  
  如果你的代码在子目录：
  ```bash
  cd poc_demo && gunicorn web_app:app
  ```

#### 环境变量（可选，但推荐）

点击 "Advanced" → "Add Environment Variable"，添加：

1. **SECRET_KEY**（推荐）
   - Key: `SECRET_KEY`
   - Value: 一个随机字符串（用于 session 加密）
   - 生成方法：运行 `python -c "import secrets; print(secrets.token_hex(32))"`

2. **PASSWORD**（可选，如果不想使用默认密码）
   - Key: `PASSWORD`
   - Value: 你的访问密码

3. **PYTHON_VERSION**（可选）
   - Key: `PYTHON_VERSION`
   - Value: `3.9.0`

⚠️ **重要**：如果你在 Root Directory 中填写了 `poc_demo`，需要确保所有路径都正确。

### 步骤 5：选择计划

- **Free**: 免费套餐（适合测试）
  - 有休眠限制（15 分钟无活动后休眠）
  - 首次启动需要几秒钟
- **Starter/Professional**: 付费套餐（无休眠，性能更好）

### 步骤 6：创建并部署

1. 点击底部 **"Create Web Service"** 按钮
2. Render 开始部署：
   - 克隆代码
   - 安装依赖
   - 启动应用
3. 等待部署完成（通常 2-5 分钟）

### 步骤 7：查看部署状态

在部署过程中，你可以：

1. **查看构建日志**：
   - 在服务页面，查看 "Logs" 标签
   - 可以看到构建和启动过程的详细信息

2. **检查部署状态**：
   - 顶部显示 "Live" 表示部署成功
   - 显示 "Build failed" 或 "Deploy failed" 表示有问题

3. **访问应用**：
   - 部署成功后，Render 会提供一个 URL，类似：
     ```
     https://agent-poc.onrender.com
     ```
   - 点击这个 URL 访问你的应用

---

## ⚙️ 配置说明

### 如果代码在子目录（poc_demo）

如果你的代码在 GitHub 仓库的 `poc_demo` 子目录中，需要修改配置：

1. **Root Directory**: 填写 `poc_demo`

2. **Build Command**:
   ```bash
   cd poc_demo && pip install -r requirements.txt
   ```

3. **Start Command**:
   ```bash
   cd poc_demo && gunicorn web_app:app
   ```

或者，更推荐的做法是：将代码移到 GitHub 仓库的根目录（参考下面的"代码结构优化"部分）。

### 数据库文件问题

⚠️ **重要**：SQLite 数据库文件（`demo.db`）通常不应该提交到 Git。

**解决方案 1：在 Render 上构建数据库**

在 Build Command 中添加数据库构建：

```bash
pip install -r requirements.txt && python db_build.py
```

**解决方案 2：将数据库文件提交到 Git**

如果数据库文件很小且不敏感，可以提交：
1. 修改 `.gitignore`，删除 `*.db` 这一行
2. 提交数据库文件
3. 推送到 GitHub

**解决方案 3：使用环境变量存储数据**

对于生产环境，建议使用 PostgreSQL（Render 提供免费 PostgreSQL 数据库）。

---

## 🐛 常见问题排查

### 1. 构建失败：找不到 requirements.txt

**问题**：`ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

**解决**：
- 检查 Root Directory 配置是否正确
- 如果代码在子目录，Build Command 中需要 `cd` 到子目录

### 2. 启动失败：找不到 web_app 模块

**问题**：`ModuleNotFoundError: No module named 'web_app'`

**解决**：
- 检查 Start Command 中的路径
- 如果代码在子目录，Start Command 中需要 `cd` 到子目录

### 3. 应用启动后立即崩溃

**问题**：应用启动但立即退出

**检查**：
- 查看 Logs，找到具体错误信息
- 常见原因：
  - 数据库文件不存在（需要在 Build Command 中构建）
  - 端口配置错误（Render 自动设置 PORT 环境变量）
  - 依赖包缺失

### 4. 静态文件 404

**问题**：CSS/JS 文件无法加载

**检查**：
- 确保 `static` 文件夹在正确位置
- 检查 `web_app.py` 中的 `static_folder` 配置

### 5. 免费套餐应用休眠

**问题**：应用访问很慢，首次加载需要等待

**说明**：这是免费套餐的正常行为，应用在 15 分钟无活动后会休眠，首次访问需要几秒钟唤醒。

**解决**：升级到付费套餐，或使用外部服务定期访问保持活跃。

---

## 📝 推荐的配置（代码在根目录）

如果你的代码直接放在 GitHub 仓库根目录，推荐配置：

**Build Command**:
```bash
pip install -r requirements.txt && python db_build.py
```

**Start Command**:
```bash
gunicorn web_app:app
```

**环境变量**:
- `SECRET_KEY`: （随机生成的密钥）
- `PASSWORD`: （可选）

---

## 📝 推荐的配置（代码在子目录 poc_demo）

如果你的代码在 `poc_demo` 子目录中：

**Root Directory**: `poc_demo`

**Build Command**:
```bash
pip install -r requirements.txt && python db_build.py
```

**Start Command**:
```bash
gunicorn web_app:app
```

**环境变量**:
- `SECRET_KEY`: （随机生成的密钥）
- `PASSWORD`: （可选）

---

## ✅ 部署成功后的步骤

1. **访问应用**：
   - 使用 Render 提供的 URL 访问
   - 输入密码登录（默认：`baa6261`，或你设置的环境变量）

2. **测试功能**：
   - 测试登录功能
   - 测试主要功能是否正常

3. **配置自定义域名**（可选）：
   - 在 Render 服务设置中
   - 点击 "Custom Domains"
   - 添加你的域名

4. **设置自动部署**：
   - Render 默认已启用自动部署
   - 每次推送到 GitHub 的 `main` 分支，Render 会自动重新部署

---

## 🔄 更新代码

当你修改代码后：

1. 在本地提交并推送：
   ```bash
   git add .
   git commit -m "更新说明"
   git push
   ```

2. Render 会自动检测更改并重新部署
3. 在 Render Dashboard 查看部署进度

---

## 🎉 完成！

部署成功后，你的应用就可以通过互联网访问了！

如有问题，可以：
- 查看 Render 的 Logs 日志
- 检查 GitHub 仓库中的代码是否正确
- 参考 Render 官方文档：https://render.com/docs
