-- ============================================
-- Supabase 数据库初始化脚本（优化版）
-- ============================================
-- 表名：gold_signals（黄金行情信号分享）
-- 用途：存储用户分享的黄金行情分析和交易信号
-- ============================================

-- 1. 创建 gold_signals 表
CREATE TABLE IF NOT EXISTS gold_signals (
    -- 基础字段
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    image_path VARCHAR(500),

    -- 用户关联字段（为未来的登录功能预留）
    author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name VARCHAR(100),

    -- 状态管理字段
    status VARCHAR(20) DEFAULT 'published' CHECK (status IN ('draft', 'published', 'archived')),

    -- 过滤和审核字段
    is_filtered BOOLEAN DEFAULT FALSE,
    filter_reason VARCHAR(200),

    -- 时间字段
    created_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,  -- 软删除

    -- 来源和通知字段
    source VARCHAR(50) DEFAULT 'telegram',
    feishu_notified BOOLEAN DEFAULT FALSE,
    qq_notified BOOLEAN DEFAULT FALSE,

    -- 统计字段（可选）
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0
);

-- 2. 创建索引（提升查询性能）
CREATE INDEX IF NOT EXISTS idx_gold_signals_created_at ON gold_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gold_signals_is_filtered ON gold_signals(is_filtered);
CREATE INDEX IF NOT EXISTS idx_gold_signals_status ON gold_signals(status);
CREATE INDEX IF NOT EXISTS idx_gold_signals_author_id ON gold_signals(author_id);
CREATE INDEX IF NOT EXISTS idx_gold_signals_deleted_at ON gold_signals(deleted_at) WHERE deleted_at IS NULL;

-- 3. 创建自动更新 updated_at 的触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_gold_signals_updated_at
    BEFORE UPDATE ON gold_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. 启用 Row Level Security (RLS)
ALTER TABLE gold_signals ENABLE ROW LEVEL SECURITY;

-- 5. 创建 RLS 策略（公开读取未删除、未过滤、已发布的帖子）
CREATE POLICY "Allow public read access to published posts"
ON gold_signals
FOR SELECT
USING (
    is_filtered = FALSE
    AND deleted_at IS NULL
    AND status = 'published'
);

-- 6. 创建 RLS 策略（允许作者查看和编辑自己的帖子）
-- 注意：这个策略在用户登录后才会生效
CREATE POLICY "Allow authors to manage their own posts"
ON gold_signals
FOR ALL
USING (auth.uid() = author_id)
WITH CHECK (auth.uid() = author_id);

-- 7. 创建 RLS 策略（允许通过 service_role 进行所有操作）
-- 注意：service_role 密钥应仅在后端使用，不应暴露给前端
CREATE POLICY "Allow all operations with service role"
ON gold_signals
FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- 插入测试数据（可选）
-- ============================================

/*
INSERT INTO gold_signals (content, status, is_filtered, created_at) VALUES
('黄金突破关键阻力位 $2050，建议关注回调买入机会。止损设在 $2040。', 'published', FALSE, NOW() - INTERVAL '5 hours'),
('今日黄金走势分析：受美联储利率决议影响，短期可能震荡。建议观望为主。', 'published', FALSE, NOW() - INTERVAL '4 hours'),
('重要提醒：黄金已进入超买区域，注意风险控制。不建议追高。', 'published', FALSE, NOW() - INTERVAL '3 hours'),
('技术分析：黄金日线形成双底形态，中长期看涨。目标位 $2100。', 'published', FALSE, NOW() - INTERVAL '2 hours'),
('市场情绪：避险情绪升温，黄金获得支撑。关注地缘政治动态。', 'published', FALSE, NOW() - INTERVAL '1 hour');
*/

-- ============================================
-- 验证表创建
-- ============================================
-- 执行以下查询验证表是否创建成功
-- SELECT * FROM gold_signals WHERE deleted_at IS NULL LIMIT 10;

-- 查看表结构
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'gold_signals'
-- ORDER BY ordinal_position;
