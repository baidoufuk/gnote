# 登录系统说明文档

## 概述

本系统实现了一套完整的用户认证和账号共享检测机制，基于 Vue 3 + Supabase Auth + Python 后端，旨在防止多人共享同一账号。

## 核心功能

### 1. 用户认证
- 使用 Supabase Auth 进行身份验证
- 用户名 + 密码登录方式
- 账号由管理员手动创建（格式：`username@internal.local`）
- 支持会话管理和自动恢复

### 2. 账号共享检测

#### 2.1 并发会话控制
- **规则**：每个账号同时只允许 1 个活跃会话
- **活跃窗口**：15 分钟（基于 `last_seen_at` 字段）
- **行为**：新登录会自动踢掉旧会话

#### 2.2 设备指纹识别
系统收集以下设备特征生成指纹：
- Canvas 指纹（权重 30%）
- Audio 指纹（权重 20%）
- 屏幕分辨率和像素比（权重 20%）
- 操作系统平台（权重 10%）
- 浏览器信息（权重 10%）
- 时区偏移（权重 5%）
- 硬件并发数（权重 5%）

#### 2.3 相似度计算
- 使用加权算法计算新旧设备指纹的相似度（0-1）
- **阈值**：相似度 < 0.5 判定为不同设备
- 存储格式：
  - `fingerprint_raw`：JSONB 格式，用于相似度计算
  - `fingerprint_hash`：SHA-256 哈希，用于快速比对

#### 2.4 风险分数系统
- **初始分数**：0 分
- **触发条件**：检测到不同设备登录时 +15 分
- **账号状态**：
  - `active`（正常）：< 40 分
  - `limited`（受限）：40-70 分
  - `banned`（封禁）：≥ 70 分

### 3. 会话管理

#### 3.1 心跳机制
- **频率**：每 60 秒
- **功能**：
  - 更新 `last_seen_at` 时间戳
  - 检查账号状态变化
  - 自动登出被封禁账号

#### 3.2 会话生命周期
```
登录 → 创建会话 → 启动心跳 → 持续更新 → 登出/超时
```

## 数据库设计

### user_profiles 表
```sql
- id: UUID (主键)
- user_id: UUID (外键 → auth.users)
- username: VARCHAR(50) (唯一)
- account_status: VARCHAR(20) (active/limited/banned)
- risk_score: INTEGER (风险分数)
- last_login_at: TIMESTAMPTZ
- created_at, updated_at, created_by, updated_by
```

### user_sessions 表
```sql
- id: UUID (主键)
- user_id: UUID (外键 → auth.users)
- fingerprint_raw: JSONB (设备指纹原始数据)
- fingerprint_hash: VARCHAR(64) (SHA-256 哈希)
- ip_address: INET
- user_agent: TEXT
- is_active: BOOLEAN
- last_seen_at: TIMESTAMPTZ (心跳更新)
- similarity_score: NUMERIC(5,2)
- kicked_reason: TEXT
```

### account_anomaly_logs 表
```sql
- id: UUID (主键)
- user_id: UUID (外键 → auth.users)
- detected_at: TIMESTAMPTZ
- event_type: VARCHAR(50) (事件类型)
- details: JSONB (详细信息)
- risk_score_change: INTEGER
- state_change: VARCHAR(20)
```

## API 端点

### POST /api/auth/login
**功能**：用户登录

**请求体**：
```json
{
  "username": "string",
  "password": "string",
  "fingerprint_raw": {
    "canvas_hash": "string",
    "audio_hash": "string",
    "screen_width": 1920,
    ...
  },
  "fingerprint_hash": "sha256_hash"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "username": "string",
      "account_status": "active",
      "risk_score": 0
    },
    "session": {
      "id": "uuid",
      "created_at": "timestamp"
    }
  }
}
```

**处理流程**：
1. Supabase Auth 验证用户名密码
2. 检查账号状态（banned 直接拒绝）
3. 查询活跃会话（15分钟内）
4. 计算设备指纹相似度
5. 如果相似度 < 0.5：
   - 增加风险分数 +15
   - 记录异常日志
6. 踢掉旧会话
7. 创建新会话
8. 更新用户资料（last_login_at, risk_score, account_status）

### POST /api/auth/logout
**功能**：用户登出

**请求体**：
```json
{
  "session_id": "uuid"
}
```

**处理流程**：
1. 设置 `is_active = false`
2. 更新 `last_seen_at`

### POST /api/auth/heartbeat
**功能**：会话心跳

**请求体**：
```json
{
  "session_id": "uuid"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "force_logout": false,
    "account_status": "active"
  }
}
```

**处理流程**：
1. 更新 `last_seen_at`
2. 检查账号状态
3. 如果 `banned`，返回 `force_logout: true`

## 前端实现

### 文件结构
```
src/
├── composables/
│   └── useAuth.js          # 认证状态管理
├── utils/
│   └── fingerprint.js      # 设备指纹收集
├── views/
│   ├── Login.vue           # 登录页面
│   └── Home.vue            # 首页（需要认证）
├── components/
│   └── Header.vue          # 头部（显示用户名和登出按钮）
└── router/
    └── index.js            # 路由配置（路由守卫）
```

### useAuth Composable
提供全局认证状态和方法：
- **状态**：`user`, `session`, `loading`, `error`, `isAuthenticated`
- **方法**：`login()`, `logout()`, `restoreSession()`, `checkAuth()`
- **心跳**：自动启动/停止 60 秒心跳定时器

### 路由守卫
```javascript
router.beforeEach((to, from, next) => {
  const { checkAuth } = useAuth()
  const isAuthenticated = checkAuth()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })  // 未登录跳转到登录页
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Home' })   // 已登录跳转到首页
  } else {
    next()
  }
})
```

## 安全特性

### 1. 防止账号共享
- 并发会话限制
- 设备指纹识别
- 风险分数累积
- 三级账号状态（active → limited → banned）

### 2. 会话安全
- 15 分钟活跃窗口
- 自动心跳检测
- 服务端时间戳（防止客户端时间篡改）
- 强制登出机制

### 3. 数据安全
- 使用 Supabase Service Role Key（服务端）
- CORS 配置
- 密码通过 Supabase Auth 加密存储
- 设备指纹双重存储（raw + hash）

## 异常检测事件

系统会记录以下异常事件到 `account_anomaly_logs` 表：

| 事件类型 | 触发条件 | 风险分数变化 |
|---------|---------|------------|
| `concurrent_login_different_device` | 相似度 < 0.5 | +15 |

## 测试场景

### 场景 1：正常登录
1. 用户首次登录
2. 创建会话，风险分数 0
3. 账号状态：active

### 场景 2：同一设备重新登录
1. 用户在同一设备再次登录
2. 计算相似度 > 0.5
3. 踢掉旧会话，创建新会话
4. 风险分数不变

### 场景 3：不同设备登录（账号共享）
1. 用户 A 在设备 A 登录
2. 用户 B 在设备 B 使用相同账号登录
3. 计算相似度 < 0.5
4. 风险分数 +15
5. 记录异常日志
6. 如果累计 ≥ 70 分，账号被封禁

### 场景 4：账号被封禁
1. 风险分数达到 70 分
2. 账号状态变为 `banned`
3. 下次心跳时强制登出
4. 无法再次登录

## 环境变量配置

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
ALLOWED_ORIGIN=*  # 生产环境应设置为具体域名
```

## 部署注意事项

1. **Supabase 配置**：
   - 确保 `auth.users` 表已创建
   - 配置 RLS 策略
   - 使用 Service Role Key（服务端）

2. **Vercel 部署**：
   - Python API 函数位于 `/api` 目录
   - 配置环境变量
   - 安装依赖：`supabase-py`

3. **前端构建**：
   - 安装依赖：`npm install`
   - 构建：`npm run build`

## 维护建议

1. **定期清理**：
   - 清理超过 15 分钟的非活跃会话
   - 归档旧的异常日志

2. **监控指标**：
   - 每日登录次数
   - 异常检测触发次数
   - 账号封禁数量

3. **风险分数衰减**（可选）：
   - 考虑实现风险分数随时间衰减机制
   - 例如：每 30 天 -5 分（最低 0 分）

## 常见问题

### Q: 为什么使用 15 分钟活跃窗口？
A: 平衡用户体验和安全性。太短会频繁踢人，太长无法及时检测共享。

### Q: 设备指纹会变化吗？
A: 会。浏览器更新、屏幕分辨率改变等都可能影响指纹。因此使用相似度而非完全匹配。

### Q: 如何解封账号？
A: 需要管理员手动修改 `user_profiles` 表的 `account_status` 和 `risk_score`。

### Q: 可以调整风险分数阈值吗？
A: 可以。修改 `api/auth/login.py` 中的阈值逻辑即可。

## 更新日志

### v1.0.0 (2026-01-29)
- 初始版本
- 实现基础认证功能
- 实现账号共享检测
- 实现风险分数系统
- 实现会话心跳机制
