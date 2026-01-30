# 用户管理指南

## 创建用户账号

由于系统采用管理员手动创建账号的模式，以下是创建用户的两种方法：

### 方法一：通过 Supabase Dashboard（推荐）

1. **登录 Supabase Dashboard**
   - 访问 https://supabase.com
   - 进入您的项目

2. **创建 Auth 用户**
   - 进入 `Authentication` → `Users`
   - 点击 `Add user` → `Create new user`
   - 填写信息：
     - Email: `username@internal.local`（例如：`zhangsan@internal.local`）
     - Password: 设置密码（至少 6 位）
     - Auto Confirm User: ✅ 勾选（跳过邮箱验证）
   - 点击 `Create user`
   - 记录生成的 User ID（UUID 格式）

3. **创建用户资料**
   - 进入 `Table Editor` → `user_profiles`
   - 点击 `Insert` → `Insert row`
   - 填写信息：
     ```
     user_id: [刚才创建的 User ID]
     username: zhangsan
     account_status: active
     risk_score: 0
     created_by: [管理员的 User ID，可以为空]
     ```
   - 点击 `Save`

### 方法二：通过 SQL 脚本

在 Supabase SQL Editor 中执行以下脚本：

```sql
-- 1. 创建 Auth 用户（需要使用 Supabase Auth Admin API）
-- 注意：这个步骤需要在应用代码中使用 Service Role Key 执行

-- 2. 假设已经创建了 Auth 用户，获得了 user_id
-- 创建用户资料
INSERT INTO user_profiles (
    user_id,
    username,
    account_status,
    risk_score,
    created_at,
    updated_at
) VALUES (
    'USER_ID_HERE',  -- 替换为实际的 User ID
    'username_here',  -- 用户名
    'active',
    0,
    NOW(),
    NOW()
);
```

### 方法三：创建管理员 API 端点（推荐用于批量创建）

创建一个管理员专用的 API 端点来创建用户：

**文件：`api/admin/create-user.py`**

```python
from http.server import BaseHTTPRequestHandler
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")  # 管理员密钥
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Secret')
        self.end_headers()

    def do_POST(self):
        try:
            # 验证管理员密钥
            admin_secret = self.headers.get('X-Admin-Secret', '')
            if not ADMIN_SECRET or admin_secret != ADMIN_SECRET:
                self.send_error_response(403, '无权限访问')
                return

            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                self.send_error_response(400, '用户名和密码不能为空')
                return

            if len(password) < 6:
                self.send_error_response(400, '密码至少 6 位')
                return

            if not supabase:
                self.send_error_response(500, 'Supabase 未初始化')
                return

            # 1. 创建 Auth 用户
            email = f"{username}@internal.local"

            try:
                auth_response = supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True  # 自动确认邮箱
                })

                if not auth_response.user:
                    self.send_error_response(500, '创建用户失败')
                    return

                user_id = auth_response.user.id
            except Exception as e:
                logger.error(f"Create auth user error: {e}")
                self.send_error_response(500, f'创建用户失败: {str(e)}')
                return

            # 2. 创建用户资料
            try:
                profile_response = supabase.table('user_profiles').insert({
                    'user_id': user_id,
                    'username': username,
                    'account_status': 'active',
                    'risk_score': 0
                }).execute()

                if not profile_response.data:
                    # 如果创建资料失败，删除 Auth 用户
                    supabase.auth.admin.delete_user(user_id)
                    self.send_error_response(500, '创建用户资料失败')
                    return

            except Exception as e:
                logger.error(f"Create profile error: {e}")
                # 删除 Auth 用户
                supabase.auth.admin.delete_user(user_id)
                self.send_error_response(500, f'创建用户资料失败: {str(e)}')
                return

            # 3. 返回成功响应
            self.send_success_response({
                'user_id': user_id,
                'username': username,
                'email': email,
                'message': '用户创建成功'
            })

        except Exception as e:
            logger.error(f"Create user error: {e}")
            self.send_error_response(500, f'服务器错误: {str(e)}')

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'data': data
        }).encode('utf-8'))

    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'error': error_message
        }).encode('utf-8'))
```

**使用方法：**

```bash
curl -X POST https://your-domain.vercel.app/api/admin/create-user \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your-admin-secret" \
  -d '{
    "username": "zhangsan",
    "password": "password123"
  }'
```

**环境变量配置：**

在 Vercel Dashboard 中添加：
```
ADMIN_SECRET=your-secure-random-string
```

## 测试账号创建示例

### 创建第一个测试账号

**方式一：Supabase Dashboard**
1. Email: `testuser@internal.local`
2. Password: `test123456`
3. Username: `testuser`

**方式二：使用 API（需要先部署并配置 ADMIN_SECRET）**
```bash
curl -X POST https://your-domain.vercel.app/api/admin/create-user \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your-admin-secret" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

## 用户管理操作

### 修改密码

系统提供两种修改密码的方式：

#### 方式一：用户自己修改密码

**API 端点**：`POST /api/auth/change-password`

**使用方法**：
```bash
curl -X POST https://your-domain.vercel.app/api/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "old_password": "old_password123",
    "new_password": "new_password456"
  }'
```

**要求**：
- 必须提供正确的旧密码
- 新密码至少 6 位
- 新密码不能与旧密码相同

**响应示例**：
```json
{
  "success": true,
  "data": {
    "message": "密码修改成功，请使用新密码重新登录"
  }
}
```

#### 方式二：管理员重置密码

**API 端点**：`POST /api/admin/reset-password`

**使用方法**：
```bash
curl -X POST https://your-domain.vercel.app/api/admin/reset-password \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your-admin-secret" \
  -d '{
    "username": "testuser",
    "new_password": "new_password123"
  }'
```

**要求**：
- 需要管理员密钥（ADMIN_SECRET）
- 不需要旧密码
- 新密码至少 6 位

**响应示例**：
```json
{
  "success": true,
  "data": {
    "username": "testuser",
    "message": "密码重置成功"
  }
}
```

#### 方式三：通过 Supabase Dashboard

1. 进入 Supabase Dashboard → Authentication → Users
2. 找到要重置密码的用户
3. 点击用户行的 `...` 菜单
4. 选择 `Reset Password`
5. 输入新密码并确认

### 查看所有用户

在 Supabase Dashboard：
- `Table Editor` → `user_profiles`

### 重置用户密码

在 Supabase Dashboard：
- `Authentication` → `Users`
- 找到用户，点击 `...` → `Reset Password`
- 或使用管理员 API：
  ```bash
  curl -X POST https://your-domain.vercel.app/api/admin/reset-password \
    -H "Content-Type: application/json" \
    -H "X-Admin-Secret: your-admin-secret" \
    -d '{
      "username": "username_here",
      "new_password": "new_password123"
    }'
  ```

### 封禁用户

```sql
UPDATE user_profiles
SET account_status = 'banned',
    status_updated_at = NOW()
WHERE username = 'username_here';
```

### 解封用户

```sql
UPDATE user_profiles
SET account_status = 'active',
    risk_score = 0,
    status_updated_at = NOW()
WHERE username = 'username_here';
```

### 查看用户登录历史

```sql
SELECT
    us.created_at,
    us.ip_address,
    us.user_agent,
    us.is_active,
    us.similarity_score,
    us.kicked_reason
FROM user_sessions us
JOIN user_profiles up ON us.user_id = up.user_id
WHERE up.username = 'username_here'
ORDER BY us.created_at DESC
LIMIT 20;
```

### 查看用户异常日志

```sql
SELECT
    aal.detected_at,
    aal.event_type,
    aal.details,
    aal.risk_score_change,
    aal.state_change
FROM account_anomaly_logs aal
JOIN user_profiles up ON aal.user_id = up.user_id
WHERE up.username = 'username_here'
ORDER BY aal.detected_at DESC;
```

## 批量用户创建脚本

如果需要批量创建用户，可以使用以下 Python 脚本：

```python
import requests
import json

API_URL = "https://your-domain.vercel.app/api/admin/create-user"
ADMIN_SECRET = "your-admin-secret"

users = [
    {"username": "user1", "password": "password123"},
    {"username": "user2", "password": "password456"},
    {"username": "user3", "password": "password789"},
]

for user in users:
    response = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "X-Admin-Secret": ADMIN_SECRET
        },
        json=user
    )

    result = response.json()
    if result.get("success"):
        print(f"✅ 创建成功: {user['username']}")
    else:
        print(f"❌ 创建失败: {user['username']} - {result.get('error')}")
```

## 安全建议

1. **ADMIN_SECRET 保护**
   - 使用强随机字符串（至少 32 位）
   - 不要提交到 Git
   - 定期更换

2. **密码策略**
   - 最少 6 位（建议 8 位以上）
   - 包含大小写字母、数字、特殊字符
   - 不使用常见密码

3. **账号审计**
   - 定期检查 `account_anomaly_logs`
   - 监控风险分数异常的账号
   - 及时处理被封禁的账号

4. **访问控制**
   - 管理员 API 仅在内网或 VPN 访问
   - 使用 IP 白名单限制访问
   - 记录所有管理操作日志

## 常见问题

### Q: 如何修改用户名？
A: 用户名存储在 `user_profiles` 表中，可以直接修改：
```sql
UPDATE user_profiles
SET username = 'new_username',
    updated_at = NOW()
WHERE username = 'old_username';
```

### Q: 忘记密码怎么办？
A: 管理员可以在 Supabase Dashboard 中重置密码，或删除用户后重新创建。

### Q: 如何删除用户？
A:
1. 在 Supabase Dashboard → Authentication → Users 中删除 Auth 用户
2. 由于设置了 `ON DELETE CASCADE`，相关的 `user_profiles`、`user_sessions`、`account_anomaly_logs` 会自动删除

### Q: 可以让用户自己注册吗？
A: 当前设计不支持。如需开放注册，需要：
1. 创建注册页面
2. 创建注册 API 端点
3. 添加邮箱验证或审核机制
4. 考虑防止恶意注册的措施
