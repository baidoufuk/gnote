# FeiShu-Frontend

阿K的分享 - 前端项目

## 项目说明

这是一个纯静态的前端项目，通过 AJAX 调用后端 API 获取数据并展示。

## 技术栈

- HTML5
- Tailwind CSS + DaisyUI
- Vanilla JavaScript (无框架)

## 文件结构

```
FeiShu-Frontend/
├── index.html          # 主页面
├── app.js              # JavaScript 逻辑
├── config.js           # 配置文件（可选）
└── README.md           # 说明文档
```

## 部署方式

### 方式一：宝塔面板 - 静态网站

1. 在宝塔面板中创建一个新的静态网站
2. 设置域名（如 `www.yourdomain.com`）
3. 将 `index.html` 和 `app.js` 上传到网站根目录
4. 修改 `app.js` 中的 `API_BASE_URL` 为后端 API 地址

### 方式二：Nginx 直接托管

```nginx
server {
    listen 80;
    server_name www.yourdomain.com;

    root /path/to/FeiShu-Frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 配置说明

在 `app.js` 文件的第 2 行，修改后端 API 地址：

```javascript
const API_BASE_URL = 'https://api.yourdomain.com'; // 改为你的后端域名
```

## 功能特性

- ✅ 响应式设计，支持移动端
- ✅ 时间轴样式展示
- ✅ 点击卡片打开模态框查看完整内容
- ✅ 支持图片展示
- ✅ 加载状态和错误提示
- ✅ 防 XSS 攻击

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 注意事项

1. 确保后端 API 已启用 CORS 支持
2. 部署前修改 `API_BASE_URL` 为实际的后端地址
3. 如果使用 HTTPS，前后端都需要配置 SSL 证书
