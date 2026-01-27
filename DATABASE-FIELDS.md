# gold_signals 表字段说明

## 📊 完整字段列表

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| **id** | SERIAL | ✅ | 自动递增 | 主键，帖子唯一标识符 |
| **content** | TEXT | ✅ | - | 帖子内容（黄金行情分析、交易信号等） |
| **image_path** | VARCHAR(500) | ❌ | NULL | 图片 URL（存储在 Supabase Storage 的图片链接） |
| **author_id** | UUID | ❌ | NULL | 作者 ID（关联到 Supabase Auth 用户表） |
| **author_name** | VARCHAR(100) | ❌ | NULL | 作者名称（冗余字段，提升查询性能） |
| **status** | VARCHAR(20) | ❌ | 'published' | 发布状态：draft（草稿）/ published（已发布）/ archived（已归档） |
| **is_filtered** | BOOLEAN | ❌ | FALSE | 是否被过滤（TRUE = 敏感内容，不公开显示） |
| **filter_reason** | VARCHAR(200) | ❌ | NULL | 过滤原因（如果被过滤，记录原因） |
| **created_at** | TIMESTAMP | ❌ | NOW() | 创建时间（帖子首次创建的时间） |
| **published_at** | TIMESTAMP | ❌ | NOW() | 发布时间（帖子正式发布的时间） |
| **updated_at** | TIMESTAMP | ❌ | NOW() | 更新时间（自动更新，通过触发器） |
| **deleted_at** | TIMESTAMP | ❌ | NULL | 删除时间（软删除，NULL = 未删除） |
| **source** | VARCHAR(50) | ❌ | 'telegram' | 来源（telegram / web / api 等） |
| **feishu_notified** | BOOLEAN | ❌ | FALSE | 是否已通知飞书（用于集成飞书机器人） |
| **qq_notified** | BOOLEAN | ❌ | FALSE | 是否已通知 QQ（用于集成 QQ 机器人） |
| **view_count** | INTEGER | ❌ | 0 | 浏览次数（统计帖子被查看的次数） |
| **like_count** | INTEGER | ❌ | 0 | 点赞数（统计帖子被点赞的次数） |

---

## 🎯 字段分类说明

### 1️⃣ 基础字段（必需）

| 字段 | 说明 | 使用场景 |
|------|------|---------|
| **id** | 主键 | 唯一标识每条帖子 |
| **content** | 帖子内容 | 存储黄金行情分析、交易建议等文本 |
| **image_path** | 图片链接 | 存储图表、截图等辅助说明图片的 URL |

**示例**：
```json
{
  "id": 1,
  "content": "黄金突破 $2050 关键阻力位，建议关注回调买入机会。",
  "image_path": "https://xxx.supabase.co/storage/v1/object/public/post-images/chart.jpg"
}
```

---

### 2️⃣ 用户关联字段（为登录功能准备）

| 字段 | 说明 | 使用场景 |
|------|------|---------|
| **author_id** | 作者 ID | 关联到 Supabase Auth，标识帖子作者 |
| **author_name** | 作者名称 | 显示作者名字，避免每次都查询用户表 |

**使用场景**：
- 未来添加用户登录后，可以显示"由 XXX 发布"
- 用户可以查看自己发布的所有帖子
- 管理员可以按作者筛选帖子

**当前状态**：暂时为 NULL（因为还没有登录功能）

---

### 3️⃣ 状态管理字段（重要）

| 字段 | 说明 | 可选值 | 使用场景 |
|------|------|--------|---------|
| **status** | 发布状态 | draft / published / archived | 控制帖子是否公开显示 |
| **is_filtered** | 是否过滤 | TRUE / FALSE | 标记敏感内容，不公开显示 |
| **filter_reason** | 过滤原因 | 文本 | 记录为什么被过滤（如"包含敏感词"） |

**工作流程**：
```
1. 创建帖子 → status = 'draft'（草稿）
2. 审核通过 → status = 'published'（发布）
3. 发现问题 → is_filtered = TRUE（过滤）
4. 不再需要 → status = 'archived'（归档）
```

**前端显示规则**：
- 只显示 `status = 'published'` 且 `is_filtered = FALSE` 且 `deleted_at IS NULL` 的帖子

---

### 4️⃣ 时间字段（自动管理）

| 字段 | 说明 | 更新方式 |
|------|------|---------|
| **created_at** | 创建时间 | 插入时自动设置，不再改变 |
| **published_at** | 发布时间 | 首次发布时设置 |
| **updated_at** | 更新时间 | 每次修改时自动更新（触发器） |
| **deleted_at** | 删除时间 | 软删除时设置为当前时间 |

**软删除说明**：
- 不真正删除数据，只设置 `deleted_at` 时间戳
- 好处：可以恢复、可以审计、可以统计
- 查询时：`WHERE deleted_at IS NULL`

---

### 5️⃣ 来源和通知字段

| 字段 | 说明 | 使用场景 |
|------|------|---------|
| **source** | 来源 | 标识帖子从哪里来（telegram / web / api） |
| **feishu_notified** | 飞书通知状态 | 避免重复通知飞书群 |
| **qq_notified** | QQ 通知状态 | 避免重复通知 QQ 群 |

**使用场景**：
- 从 Telegram Bot 接收消息 → `source = 'telegram'`
- 从网页后台发布 → `source = 'web'`
- 通知飞书后 → `feishu_notified = TRUE`

---

### 6️⃣ 统计字段（可选）

| 字段 | 说明 | 使用场景 |
|------|------|---------|
| **view_count** | 浏览次数 | 统计帖子热度 |
| **like_count** | 点赞数 | 用户互动统计 |

**未来功能**：
- 显示"已有 123 人查看"
- 按热度排序
- 统计最受欢迎的帖子

---

## 🔍 常见查询示例

### 1. 获取所有公开帖子
```sql
SELECT * FROM gold_signals
WHERE status = 'published'
  AND is_filtered = FALSE
  AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### 2. 获取某个作者的所有帖子
```sql
SELECT * FROM gold_signals
WHERE author_id = 'user-uuid-here'
  AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### 3. 获取草稿帖子
```sql
SELECT * FROM gold_signals
WHERE status = 'draft'
  AND deleted_at IS NULL;
```

### 4. 软删除一条帖子
```sql
UPDATE gold_signals
SET deleted_at = NOW()
WHERE id = 123;
```

### 5. 恢复被删除的帖子
```sql
UPDATE gold_signals
SET deleted_at = NULL
WHERE id = 123;
```

---

## 💡 设计理念

### 为什么使用软删除？
- ✅ 可以恢复误删的数据
- ✅ 保留历史记录用于审计
- ✅ 不影响关联数据的完整性

### 为什么有 created_at 和 published_at？
- `created_at`：帖子首次创建的时间（可能是草稿）
- `published_at`：帖子正式发布的时间（对外可见）
- 用途：区分"创建"和"发布"两个时间点

### 为什么 author_name 是冗余字段？
- 避免每次查询都要 JOIN 用户表
- 提升查询性能（特别是列表页）
- 即使用户改名，历史帖子仍显示发布时的名字

---

## 🎯 未来扩展建议

如果以后需要更多功能，可以考虑增加：

| 字段 | 类型 | 说明 |
|------|------|------|
| **title** | VARCHAR(200) | 帖子标题（如果需要标题+内容的结构） |
| **tags** | TEXT[] | 标签数组（如 ['黄金', '技术分析', '做多']） |
| **category** | VARCHAR(50) | 分类（如 '黄金', '白银', '原油'） |
| **priority** | INTEGER | 优先级（置顶功能） |
| **comment_count** | INTEGER | 评论数 |
| **share_count** | INTEGER | 分享次数 |

---

**当前表结构已经为未来功能做好准备！** 🎉
