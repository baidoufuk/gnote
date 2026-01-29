# Vercel 部署指南

本文档详细说明如何将项目部署到 Vercel。

## 前置准备

### 1. 创建 Supabase 数据库

1. 访问 [Supabase](https://supabase.com/) 并创建账号
2. 创建新项目
3. 在 SQL Editor 中执行以下 SQL 创建表：

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    image_path VARCHAR(500),
    source VARCHAR(50) DEFAULT 'telegram',
    is_filtered BOOLEAN DEFAULT FALSE,
    filter_reason VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    feishu_notified BOOLEAN DEFAULT FALSE,
    qq_notified BOOLEAN DEFAULT FALSE
);

-- 创建索引
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_is_filtered ON posts(is_filtered);
```

4. 获取项目的 URL 和 API Key
   - 进入 Settings → API
   - 复制 `Project URL` 和 `anon public` key

### 2. 准备 Vercel 账号

1. 访问 [Vercel](https://vercel.com/) 并注册账号
2. 建议使用 GitHub 账号登录，方便后续自动部署

## 部署方式

### 方式一：通过 Vercel Dashboard（推荐）

#### 步骤 1：推送代码到 GitHub

```bash
# 如果还没有初始化 Git
git init
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库后，推送代码
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

#### 步骤 2：在 Vercel 中导入项目

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "Add New..." → "Project"
3. 选择你的 GitHub 仓库
4. Vercel 会自动检测到这是一个 Vite 项目

#### 步骤 3：配置环境变量

在 Vercel 项目设置中添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SUPABASE_URL` | 你的 Supabase URL | 从 Supabase Dashboard 获取 |
| `SUPABASE_KEY` | 你的 Supabase Anon Key | 从 Supabase Dashboard 获取 |
| `TELEGRAM_WEBHOOK_SECRET` | 自定义密钥 | 可选，用于 Telegram Webhook |

#### 步骤 4：部署

点击 "Deploy" 按钮，Vercel 会自动：
1. 安装 Node.js 依赖
2. 构建 Vue 前端
3. 部署 Python Serverless Functions
4. 分配域名

部署完成后，你会得到一个类似 `https://your-project.vercel.app` 的域名。

---

### 方式二：通过 Vercel CLI

#### 步骤 1：安装 Vercel CLI

```bash
npm install -g vercel
```

#### 步骤 2：登录 Vercel

```bash
vercel login
```

#### 步骤 3：部署

在项目根目录运行：

```bash
vercel
```

按照提示完成部署：
- 选择或创建项目
- 确认项目设置
- 等待部署完成

#### 步骤 4：配置环境变量

```bash
# 添加 Supabase URL
vercel env add SUPABASE_URL

# 添加 Supabase Key
vercel env add SUPABASE_KEY

# 添加 Telegram Webhook Secret（可选）
vercel env add TELEGRAM_WEBHOOK_SECRET
```

添加环境变量后，需要重新部署：

```bash
vercel --prod
```

---

## 配置 Telegram Bot（可选）

如果需要使用 Telegram Bot 功能：

### 1. 获取部署 URL

部署完成后，你会得到一个 Vercel URL，例如：
```
https://your-project.vercel.app
```

### 2. 设置 Telegram Webhook

使用以下命令设置 Webhook：

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-project.vercel.app/api/webhook",
    "secret_token": "your-webhook-secret"
  }'
```

**注意**：
- 将 `<YOUR_BOT_TOKEN>` 替换为你的 Telegram Bot Token
- 将 `your-project.vercel.app` 替换为你的实际域名
- 将 `your-webhook-secret` 替换为你在环境变量中设置的密钥

### 3. 验证 Webhook

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

---

## 验证部署

### 1. 检查前端

访问你的 Vercel 域名，应该能看到：
- 页面正常加载
- 友情提示弹窗显示
- 帖子列表加载（如果数据库有数据）

### 2. 检查 API

访问 `https://your-project.vercel.app/api/posts`，应该返回 JSON 数据：

```json
{
  "success": true,
  "count": 0,
  "data": []
}
```

---

## 自动部署

配置完成后，每次推送代码到 GitHub 的 main 分支，Vercel 会自动：
1. 检测到代码变更
2. 重新构建项目
3. 自动部署到生产环境

---

## 常见问题

### Q: 部署后 API 返回 500 错误

**A**: 检查环境变量是否正确配置：
1. 进入 Vercel Dashboard → 你的项目 → Settings → Environment Variables
2. 确认 `SUPABASE_URL` 和 `SUPABASE_KEY` 已正确设置
3. 重新部署项目

### Q: 前端无法连接到 API

**A**: 检查以下几点：
1. 确认 API 路由正确：`/api/posts`
2. 检查浏览器控制台是否有 CORS 错误
3. 确认 Serverless Functions 已正确部署

### Q: Telegram Webhook 不工作

**A**: 检查以下几点：
1. 确认 `TELEGRAM_WEBHOOK_SECRET` 环境变量已设置
2. 确认 Webhook URL 正确
3. 使用 `getWebhookInfo` 检查 Webhook 状态
4. 查看 Vercel 的 Function Logs

### Q: 构建失败

**A**: 常见原因：
1. Node.js 版本不兼容 - 在 `package.json` 中指定版本
2. 依赖安装失败 - 检查 `package.json` 中的依赖
3. 构建命令错误 - 确认 `vercel.json` 配置正确

---

## 性能优化建议

### 1. 启用 Vercel Analytics

在 Vercel Dashboard 中启用 Analytics，监控：
- 页面加载时间
- API 响应时间
- 用户访问量

### 2. 配置缓存

在 `vercel.json` 中添加缓存配置：

```json
{
  "headers": [
    {
      "source": "/api/posts",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=60, stale-while-revalidate"
        }
      ]
    }
  ]
}
```

### 3. 优化图片

如果使用图片，建议：
- 使用 Vercel Image Optimization
- 压缩图片大小
- 使用 WebP 格式

---

## 监控和日志

### 查看 Function Logs

1. 进入 Vercel Dashboard → 你的项目
2. 点击 "Functions" 标签
3. 选择具体的 Function 查看日志

### 查看部署日志

1. 进入 Vercel Dashboard → 你的项目
2. 点击 "Deployments" 标签
3. 选择具体的部署查看构建日志

---

## 成本说明

Vercel 免费套餐包括：
- ✅ 100 GB 带宽/月
- ✅ 100 GB-小时 Serverless Function 执行时间
- ✅ 无限部署
- ✅ 自动 HTTPS
- ✅ 全球 CDN

对于个人项目，免费套餐完全够用。

---

## 技术支持

如有问题，可以：
1. 查看 [Vercel 文档](https://vercel.com/docs)
2. 查看 [Supabase 文档](https://supabase.com/docs)
3. 在项目 GitHub 仓库提 Issue
