-- ============================================
-- Supabase 数据库初始化脚本
-- ============================================
-- 用途：创建 posts 表及相关索引
-- 使用方法：在 Supabase Dashboard → SQL Editor 中执行此脚本
-- ============================================

-- 1. 创建 posts 表
CREATE TABLE IF NOT EXISTS posts (
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

-- 2. 创建索引（提升查询性能）
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_is_filtered ON posts(is_filtered);

-- 3. 启用 Row Level Security (RLS)
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 4. 创建 RLS 策略（允许所有人读取未过滤的帖子）
CREATE POLICY "Allow public read access to unfiltered posts"
ON posts
FOR SELECT
USING (is_filtered = FALSE);

-- 5. 创建 RLS 策略（允许通过 anon key 插入数据）
-- 注意：这允许任何使用 anon key 的客户端插入数据
-- 如果需要更严格的控制，应该使用认证系统
CREATE POLICY "Allow insert with anon key"
ON posts
FOR INSERT
WITH CHECK (true);

-- 6. 创建 RLS 策略（允许通过 anon key 更新数据）
CREATE POLICY "Allow update with anon key"
ON posts
FOR UPDATE
USING (true)
WITH CHECK (true);

-- 7. 创建 RLS 策略（允许通过 service_role 进行所有操作）
-- 注意：这个策略只在使用 service_role key 时生效
CREATE POLICY "Allow all operations with service role"
ON posts
FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================
-- 插入测试数据（可选）
-- ============================================
-- 如果需要测试数据，取消下面的注释

/*
INSERT INTO posts (content, image_path, is_filtered, created_at) VALUES
('欢迎来到阿K的分享！这是第一条测试帖子。', NULL, FALSE, NOW() - INTERVAL '5 hours'),
('今天分享一个学习心得：持续学习比一次性学很多更重要。每天进步一点点，长期坚持下来效果会很明显。', NULL, FALSE, NOW() - INTERVAL '4 hours'),
('关于时间管理的思考：
1. 优先处理重要且紧急的事
2. 学会说不，拒绝不必要的干扰
3. 给自己留出思考和休息的时间
4. 定期回顾和调整计划', NULL, FALSE, NOW() - INTERVAL '3 hours'),
('今天看到一句话很有感触：成功不是终点，失败也不是终结，唯有勇气才是永恒。

分享给大家，希望我们都能在困难面前保持勇气和信心。', NULL, FALSE, NOW() - INTERVAL '2 hours'),
('健康提醒：长时间对着电脑工作要注意休息。建议每小时起来活动5-10分钟，做做眼保健操，伸展一下身体。身体是革命的本钱！', NULL, FALSE, NOW() - INTERVAL '1 hour');
*/

-- ============================================
-- 验证表创建
-- ============================================
-- 执行以下查询验证表是否创建成功
-- SELECT * FROM posts LIMIT 10;

-- 查看表结构
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'posts'
-- ORDER BY ordinal_position;
