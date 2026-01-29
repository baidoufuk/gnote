# 项目文档索引

本目录包含项目的所有技术文档和说明。

## 文档列表

### 系统设计与架构
- [LOGIN-SYSTEM.md](./LOGIN-SYSTEM.md) - 登录系统完整说明文档
  - 用户认证机制
  - 账号共享检测算法
  - 设备指纹识别
  - 风险分数系统
  - API 端点说明
  - 数据库设计
- [USER-MANAGEMENT.md](./USER-MANAGEMENT.md) - 用户管理指南
  - 创建用户账号（三种方法）
  - 用户管理操作（封禁、解封、重置密码）
  - 批量创建脚本
  - 安全建议

### 数据库相关
- [DATABASE-FIELDS.md](./DATABASE-FIELDS.md) - 数据库字段说明
- [MIGRATION.md](./MIGRATION.md) - 数据库迁移指南

### 部署与运维
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南
  - Vercel 部署配置
  - 环境变量设置
  - 域名配置

### 前端开发
- [README-VUE.md](./README-VUE.md) - Vue 3 项目说明
  - 项目结构
  - 开发指南
  - 组件说明

### UI/UX 设计
- [DESIGN-IMPROVEMENTS.md](./DESIGN-IMPROVEMENTS.md) - 设计改进建议
- [MOBILE-OPTIMIZATION.md](./MOBILE-OPTIMIZATION.md) - 移动端优化方案

## 快速导航

### 新手入门
1. 阅读 [README-VUE.md](./README-VUE.md) 了解项目结构
2. 阅读 [DEPLOYMENT.md](./DEPLOYMENT.md) 配置开发环境
3. 阅读 [LOGIN-SYSTEM.md](./LOGIN-SYSTEM.md) 了解认证系统

### 开发者
- 数据库操作：参考 [DATABASE-FIELDS.md](./DATABASE-FIELDS.md) 和 [MIGRATION.md](./MIGRATION.md)
- 登录功能：参考 [LOGIN-SYSTEM.md](./LOGIN-SYSTEM.md)
- UI 优化：参考 [DESIGN-IMPROVEMENTS.md](./DESIGN-IMPROVEMENTS.md) 和 [MOBILE-OPTIMIZATION.md](./MOBILE-OPTIMIZATION.md)

### 运维人员
- 部署流程：[DEPLOYMENT.md](./DEPLOYMENT.md)
- 账号管理：[LOGIN-SYSTEM.md](./LOGIN-SYSTEM.md) 的"维护建议"章节

## 文档维护

- 所有文档使用 Markdown 格式
- 更新文档时请同步更新本索引文件
- 重要变更请在对应文档的"更新日志"章节记录
