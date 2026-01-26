# FeiShu-Frontend (Vue 3 版本)

阿K的分享 - Vue 3 前端项目

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios

## 项目结构

```
FeiShu-Frontend/
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css          # Tailwind CSS 入口
│   ├── components/
│   │   ├── Header.vue            # 头部组件
│   │   ├── PostCard.vue          # 帖子卡片组件
│   │   ├── PostModal.vue         # 帖子详情模态框
│   │   └── PostList.vue          # 帖子列表组件
│   ├── composables/
│   │   └── usePosts.js           # 帖子数据管理
│   ├── utils/
│   │   ├── api.js                # API 请求封装
│   │   └── format.js             # 工具函数
│   ├── App.vue                   # 根组件
│   └── main.js                   # 入口文件
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── vercel.json                   # Vercel 部署配置
```

## 本地开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 部署到 Vercel

### 方式一：通过 Vercel CLI

1. 安装 Vercel CLI

```bash
npm install -g vercel
```

2. 登录 Vercel

```bash
vercel login
```

3. 部署项目

```bash
vercel
```

### 方式二：通过 Vercel 网站

1. 访问 [Vercel](https://vercel.com)
2. 点击 "Import Project"
3. 选择你的 Git 仓库
4. Vercel 会自动检测 Vite 项目并配置构建设置
5. 点击 "Deploy"

### 环境变量配置

如果需要修改后端 API 地址，可以在 Vercel 项目设置中添加环境变量：

- 变量名: `VITE_API_BASE_URL`
- 变量值: 你的后端 API 地址

然后修改 [src/utils/api.js](src/utils/api.js:2) 中的 API_BASE_URL：

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://tofuali.top'
```

## 功能特性

- ✅ Vue 3 Composition API
- ✅ 响应式设计，支持移动端
- ✅ 时间轴样式展示
- ✅ Element Plus 模态框组件
- ✅ 支持图片展示
- ✅ 加载状态和错误提示
- ✅ Tailwind CSS 样式
- ✅ Vite 快速开发体验
- ✅ 适配 Vercel 部署

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 注意事项

1. 确保后端 API 已启用 CORS 支持
2. 如果使用 HTTPS，前后端都需要配置 SSL 证书
3. Vercel 部署时会自动处理环境变量和构建配置

## 从旧版本迁移

原 Vanilla JavaScript 版本已备份为 [index-old.html](index-old.html) 和 [app.js](app.js)。

## License

MIT
