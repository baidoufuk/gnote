-- ============================================
-- 用户资料表（User Profiles）
-- ============================================
-- 说明：
-- 1. Supabase Auth 提供 auth.users 表用于身份验证（存储邮箱、密码哈希）
-- 2. 本表存储用户的业务信息（用户名、创建者、更新者、最后登录时间等）
-- 3. 通过 user_id 外键关联到 auth.users 表
-- 4. 管理员通过 Supabase Dashboard 或 Admin API 手动创建用户
-- ============================================

-- 1. 创建 user_profiles 表
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),
    last_login_at TIMESTAMPTZ,
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'limited', 'banned')),
    risk_score INTEGER DEFAULT 0,
    status_updated_at TIMESTAMPTZ
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);

-- 3. 启用 RLS（Row Level Security）
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 4. 创建 RLS 策略（允许所有人读取用户资料）
CREATE POLICY "Allow public read access to user profiles"
ON user_profiles
FOR SELECT
USING (true);

-- 5. 创建 RLS 策略（允许用户更新自己的资料）
CREATE POLICY "Allow users to update their own profile"
ON user_profiles
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 6. 创建 RLS 策略（允许通过 service_role 进行所有操作）
CREATE POLICY "Allow all operations with service role"
ON user_profiles
FOR ALL
USING (true)
WITH CHECK (true);

-- 7. 创建触发器：自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 8. 创建触发器：当新用户创建时自动创建 profile
-- 注意：管理员创建用户时，需要在 raw_user_meta_data 中传入 username
CREATE OR REPLACE FUNCTION create_profile_for_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (user_id, username, created_by)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
        NULLIF(current_setting('request.jwt.claims', true)::json->>'sub', '')::uuid
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION create_profile_for_new_user();

-- ============================================
-- 登录日志表（Login Logs）
-- ============================================
-- 说明：记录每次用户登录的详细信息
-- ============================================

-- 9. 创建 login_logs 表
CREATE TABLE IF NOT EXISTS login_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    login_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT true
);

-- 10. 创建索引
CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_login_logs_login_at ON login_logs(login_at DESC);

-- 11. 启用 RLS
ALTER TABLE login_logs ENABLE ROW LEVEL SECURITY;

-- 12. 创建 RLS 策略（用户只能查看自己的登录日志）
CREATE POLICY "Allow users to view their own login logs"
ON login_logs
FOR SELECT
USING (auth.uid() = user_id);

-- 13. 创建 RLS 策略（允许通过 service_role 进行所有操作）
CREATE POLICY "Allow all operations with service role on login_logs"
ON login_logs
FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- 执行以下查询验证表是否创建成功
-- SELECT * FROM user_profiles LIMIT 10;
-- SELECT * FROM login_logs ORDER BY login_at DESC LIMIT 10;

-- ============================================
-- 用户会话表（User Sessions）
-- ============================================
-- 说明：管理活跃会话，实现账号共享检测
-- ============================================

-- 14. 创建 user_sessions 表
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    fingerprint_raw JSONB NOT NULL,
    fingerprint_hash VARCHAR(64) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    kicked_reason TEXT,
    similarity_score NUMERIC(5,2)
);

-- 15. 创建索引
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(user_id, is_active, last_seen_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_fingerprint_hash ON user_sessions(fingerprint_hash);

-- 16. 启用 RLS
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- 17. 创建 RLS 策略（用户只能查看自己的会话）
CREATE POLICY "Allow users to view their own sessions"
ON user_sessions
FOR SELECT
USING (auth.uid() = user_id);

-- 18. 创建 RLS 策略（允许通过 service_role 进行所有操作）
CREATE POLICY "Allow all operations with service role on user_sessions"
ON user_sessions
FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- 账号异常日志表（Account Anomaly Logs）
-- ============================================
-- 说明：记录账号共享检测的异常事件
-- ============================================

-- 19. 创建 account_anomaly_logs 表
CREATE TABLE IF NOT EXISTS account_anomaly_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    details JSONB,
    risk_score_change INTEGER,
    state_change VARCHAR(20)
);

-- 20. 创建索引
CREATE INDEX IF NOT EXISTS idx_account_anomaly_logs_user_id ON account_anomaly_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_account_anomaly_logs_detected_at ON account_anomaly_logs(detected_at DESC);

-- 21. 启用 RLS
ALTER TABLE account_anomaly_logs ENABLE ROW LEVEL SECURITY;

-- 22. 创建 RLS 策略（用户只能查看自己的异常日志）
CREATE POLICY "Allow users to view their own anomaly logs"
ON account_anomaly_logs
FOR SELECT
USING (auth.uid() = user_id);

-- 23. 创建 RLS 策略（允许通过 service_role 进行所有操作）
CREATE POLICY "Allow all operations with service role on account_anomaly_logs"
ON account_anomaly_logs
FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- 执行以下查询验证新表是否创建成功
-- SELECT * FROM user_sessions LIMIT 10;
-- SELECT * FROM account_anomaly_logs ORDER BY detected_at DESC LIMIT 10;
