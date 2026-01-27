# 飞书内容发布系统 - Vercel Serverless 版本

阿K的分享 - 前后端一体化项目（部署在 Vercel）

## 项目说明

这是一个部署在 Vercel 上的前后端一体化项目，使用 Vue 3 前端框架、Serverless Functions 和 Supabase 数据库。

## 技术栈

**前端**：
- Vue 3 (Composition API)
- Element Plus (UI 组件库)
- Tailwind CSS (样式框架)
- Vite (构建工具)
- Axios (HTTP 客户端)

**后端**：
- Vercel Serverless Functions (Python)
- Supabase (PostgreSQL 数据库)

## 项目结构

```
FeiShu-Frontend/
├── src/                    # Vue 3 前端源码
│   ├── components/        # Vue 组件
│   │   ├── Header.vue    # 页面头部
│   │   ├── PostCard.vue  # 帖子卡片
│   │   ├── PostList.vue  # 帖子列表
│   │   └── PostModal.vue # 帖子详情弹窗
│   ├── composables/      # 组合式函数
│   │   └── usePosts.js   # 帖子数据管理
│   ├── utils/            # 工具函数
│   │   ├── api.js        # API 请求封装
│   │   └── format.js     # 格式化工具
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── api/                   # Serverless Functions（后端 API）
│   ├── posts.py          # GET /api/posts - 获取帖子列表
│   └── webhook.py        # POST /api/webhook - Telegram Webhook
├── public/               # 静态资源
├── index.html            # HTML 入口
├── package.json          # Node.js 依赖
├── vite.config.js        # Vite 配置
├── tailwind.config.js    # Tailwind CSS 配置
├── vercel.json           # Vercel 配置
├── requirements.txt      # Python 依赖
├── .env                  # 环境变量（不提交到 Git）
└── .env.example          # 环境变量示例
```

## 部署步骤

### 1. 创建 Supabase 数据库

1. 访问 [Supabase](https://supabase.com/) 并创建账号
2. 创建新项目
3. 在 SQL Editor 中执行 `database-setup.sql` 文件中的 SQL 语句创建表

**重要**：请使用项目根目录的 [database-setup.sql](database-setup.sql) 文件，它包含了完整的表结构和安全策略。

主要表：`gold_signals`（黄金行情信号分享）

4. 获取项目的 URL 和 API Key（在 Settings → API）

### 2. 部署到 Vercel

1. 安装 Vercel CLI（如果还没安装）：
   ```bash
   npm install -g vercel
   ```

2. 在项目目录中运行：
   ```bash
   vercel
   ```

3. 按照提示完成部署

4. 在 Vercel Dashboard 中配置环境变量：
   - `SUPABASE_URL`: 你的 Supabase 项目 URL
   - `SUPABASE_KEY`: 你的 Supabase Anon Key
   - `TELEGRAM_WEBHOOK_SECRET`: Telegram Webhook 密钥（可选）

### 3. 配置 Telegram Bot（可选）

如果需要使用 Telegram Bot 功能：

1. 获取你的 Vercel 部署 URL（如 `https://your-project.vercel.app`）
2. 设置 Telegram Webhook：
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-project.vercel.app/api/webhook"}'
   ```

## API 接口

### GET /api/posts

获取帖子列表

**查询参数**：
- `limit`: 返回数量限制（默认 100，最大 1000）

**响应示例**：
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "id": 1,
      "content": "帖子内容",
      "image_path": null,
      "source": "telegram",
      "is_filtered": false,
      "filter_reason": null,
      "created_at": "2024-01-01T00:00:00Z",
      "feishu_notified": false,
      "qq_notified": false
    }
  ]
}
```

### POST /api/webhook

Telegram Webhook 接口（需要配置 Telegram Bot）

## 本地开发

### 1. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装 Python 依赖（用于本地测试 Serverless Functions）
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Supabase 配置：
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
```

### 3. 本地运行

**方式一：仅运行前端（推荐用于前端开发）**
```bash
npm run dev
```
访问 `http://localhost:5173`

**方式二：运行完整项目（前端 + Serverless Functions）**
```bash
# 需要先安装 Vercel CLI
npm install -g vercel

# 运行完整项目
vercel dev
```
访问 `http://localhost:3000`

### 4. 构建项目

```bash
npm run build
```

构建产物会输出到 `dist/` 目录。

## 功能特性

- ✅ 现代化 Vue 3 架构（Composition API）
- ✅ Element Plus 企业级 UI 组件
- ✅ 响应式设计，完美支持移动端和 PC
- ✅ 时间轴样式展示，美观优雅
- ✅ 点击卡片打开模态框查看完整内容
- ✅ 支持图片展示
- ✅ 加载状态和错误提示
- ✅ 防 XSS 攻击
- ✅ 前后端一体化部署
- ✅ Serverless 架构，按需付费
- ✅ 自动 HTTPS 和全球 CDN
- ✅ 友情提示弹窗（每次刷新显示）

## 优势

- ✅ **不需要备案**（Vercel 在国外）
- ✅ **自动 HTTPS**（免费 SSL 证书）
- ✅ **全球 CDN**（访问速度快）
- ✅ **免费套餐**（足够个人项目使用）
- ✅ **自动部署**（Git push 即部署）
- ✅ **前后端一体化**（无需分别部署）

## 注意事项

- Vercel Serverless Functions 有执行时间限制（免费版 10 秒）
- 如果没有配置 Supabase，API 会返回假数据用于测试
- 前端会自动使用相对路径调用 API，无需配置域名
- 部署在 Vercel 上不需要域名备案（服务器在国外）

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
