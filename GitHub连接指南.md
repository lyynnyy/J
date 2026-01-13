# GitHub 仓库连接指南

本指南将帮助你将项目代码推送到 GitHub 并连接到部署平台。

---

## 📋 前提条件

1. **GitHub 账号**：如果没有，请先访问 https://github.com 注册
2. **Git 已安装**：检查是否已安装 Git
   ```bash
   git --version
   ```
   如果没有安装，请访问 https://git-scm.com/downloads 下载安装

---

## 🚀 步骤一：创建 GitHub 仓库

### 方法 1：在 GitHub 网站上创建（推荐）

1. **登录 GitHub**
   - 访问 https://github.com 并登录

2. **创建新仓库**
   - 点击右上角的 "+" 号
   - 选择 "New repository"

3. **填写仓库信息**
   - **Repository name**: `agent-poc`（或任意名称）
   - **Description**: 分析型智能体 Web POC（可选）
   - **Visibility**: 
     - Public（公开，免费）
     - Private（私有，需要付费，但学生可免费）
   - ⚠️ **不要**勾选 "Initialize this repository with a README"（因为我们已有代码）

4. **点击 "Create repository"**
   - 创建成功后，GitHub 会显示仓库地址，类似：
     ```
     https://github.com/你的用户名/agent-poc.git
     ```

---

## 🔧 步骤二：初始化本地 Git 仓库

在项目目录中执行以下命令：

### 1. 进入项目目录
```bash
cd "/Users/lynn/智能体/Agent_v4_多工具/poc_demo"
```

### 2. 初始化 Git 仓库
```bash
git init
```

### 3. 添加所有文件到暂存区
```bash
git add .
```

### 4. 创建第一次提交
```bash
git commit -m "Initial commit: Flask 应用和部署配置"
```

---

## 🔗 步骤三：连接到 GitHub 仓库

### 1. 添加远程仓库地址

将下面的 `你的用户名` 和 `仓库名` 替换为你的实际信息：

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
```

例如：
```bash
git remote add origin https://github.com/zhangsan/agent-poc.git
```

### 2. 验证远程仓库
```bash
git remote -v
```

应该显示：
```
origin  https://github.com/你的用户名/仓库名.git (fetch)
origin  https://github.com/你的用户名/仓库名.git (push)
```

---

## 📤 步骤四：推送代码到 GitHub

### 1. 推送到 GitHub
```bash
git branch -M main
git push -u origin main
```

### 2. 输入 GitHub 凭证

如果是第一次推送，GitHub 会要求你输入用户名和密码：
- **用户名**：你的 GitHub 用户名
- **密码**：需要使用 **Personal Access Token**（不是 GitHub 密码）

#### 如何创建 Personal Access Token：

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写信息：
   - **Note**: `部署平台访问`（任意描述）
   - **Expiration**: 选择过期时间（或 No expiration）
   - **Select scopes**: 勾选 `repo`（全选 Repository 权限）
4. 点击 "Generate token"
5. **复制生成的 token**（只显示一次，务必保存）

在命令行中输入用户名，密码处粘贴 token。

---

## ✅ 验证推送成功

1. **刷新 GitHub 网页**
   - 访问你的仓库页面
   - 应该能看到所有文件

2. **检查文件**
   - 确认重要文件都在（如 `web_app.py`、`requirements.txt` 等）
   - 确认 `.gitignore` 生效（不应该看到 `demo.db`、`__pycache__` 等）

---

## 🔄 后续更新代码

当你修改代码后，使用以下命令更新 GitHub：

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 推送到 GitHub
git push
```

---

## 🎯 步骤五：在部署平台连接 GitHub

### Render 平台：

1. 登录 Render（https://render.com）
2. 点击 "New" → "Web Service"
3. 选择 "Build and deploy from a Git repository"
4. 点击 "Connect account" 连接 GitHub
5. 授权 Render 访问 GitHub
6. 选择你的仓库（如 `agent-poc`）
7. 点击 "Connect"
8. 配置部署设置（见部署指南）
9. 点击 "Create Web Service"

### Railway 平台：

1. 登录 Railway（https://railway.app）
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 Railway 访问 GitHub
5. 选择你的仓库
6. Railway 会自动检测并部署

---

## 🐛 常见问题

### 1. 推送时提示需要认证

**问题**：`remote: Support for password authentication was removed`

**解决**：使用 Personal Access Token 代替密码

### 2. 想要更改远程仓库地址

```bash
# 查看当前远程地址
git remote -v

# 更改远程地址
git remote set-url origin https://github.com/新用户名/新仓库名.git
```

### 3. 忘记添加 .gitignore，已提交了不应该提交的文件

```bash
# 从 Git 中删除文件（但保留本地文件）
git rm --cached demo.db
git rm -r --cached __pycache__

# 提交更改
git commit -m "Remove files that should be ignored"

# 推送到 GitHub
git push
```

### 4. 想要撤销最后一次提交

```bash
# 撤销提交但保留更改
git reset --soft HEAD~1

# 或完全撤销（谨慎使用）
git reset --hard HEAD~1
```

---

## 📝 快速命令参考

```bash
# 初始化仓库
git init

# 查看状态
git status

# 添加文件
git add .

# 提交更改
git commit -m "提交说明"

# 添加远程仓库
git remote add origin https://github.com/用户名/仓库名.git

# 推送代码
git push -u origin main

# 查看远程仓库
git remote -v

# 拉取最新代码
git pull
```

---

## 🎉 完成！

代码已成功推送到 GitHub 后，你就可以：

1. ✅ 在任何地方访问你的代码
2. ✅ 与他人协作
3. ✅ 连接到部署平台自动部署
4. ✅ 使用版本控制管理代码

需要帮助吗？遇到问题可以查看 GitHub 官方文档：https://docs.github.com
