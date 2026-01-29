from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 配置
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
# 优先使用 service_role key（服务端安全），否则使用 anon key
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or os.environ.get("SUPABASE_KEY", "")
IS_DEVELOPMENT = os.environ.get("VERCEL_ENV") != "production"

# 初始化 Supabase 客户端
supabase = None
logger.info({
    "event": "env_loaded",
    "has_url": bool(SUPABASE_URL),
    "has_service_role": bool(SUPABASE_SERVICE_ROLE_KEY),
    "vercel_env": os.environ.get("VERCEL_ENV"),
})
print("[posts.py] Env loaded:", json.dumps({
    "has_url": bool(SUPABASE_URL),
    "has_service_role": bool(SUPABASE_SERVICE_ROLE_KEY),
    "vercel_env": os.environ.get("VERCEL_ENV"),
}))
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
        print("[posts.py] Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        print(f"[posts.py] Failed to initialize Supabase: {e}")
else:
    logger.warning("Supabase env vars missing, unable to initialize client")
    print("[posts.py] Supabase env vars missing, client not initialized")


def get_fake_posts():
    """生成假数据用于开发测试（仅在开发环境使用）"""
    base_time = datetime.utcnow()
    fake_contents = [
        "今天市场波动较大，建议大家保持冷静，理性分析。记住投资有风险，入市需谨慎。不要盲目跟风，要根据自己的实际情况做决策。",
        "分享一个学习心得：持续学习比一次性学很多更重要。每天进步一点点，长期坚持下来效果会很明显。\n\n推荐大家养成每天阅读的习惯，哪怕只有15分钟。",
        "关于时间管理的思考：\n1. 优先处理重要且紧急的事\n2. 学会说不，拒绝不必要的干扰\n3. 给自己留出思考和休息的时间\n4. 定期回顾和调整计划",
        "今天看到一句话很有感触：成功不是终点，失败也不是终结，唯有勇气才是永恒。\n\n分享给大家，希望我们都能在困难面前保持勇气和信心。",
        "健康提醒：长时间对着电脑工作要注意休息。建议每小时起来活动5-10分钟，做做眼保健操，伸展一下身体。身体是革命的本钱！",
        "分享一个提高效率的小技巧：使用番茄工作法。\n\n工作25分钟，休息5分钟，4个番茄后休息15-30分钟。这样可以保持专注，避免疲劳。",
        "今天的思考：不要把所有鸡蛋放在一个篮子里。无论是投资、职业发展还是人际关系，多元化都很重要。\n\n保持开放的心态，不断学习新技能，拓展新领域。",
        "关于阅读的建议：\n- 选择适合自己水平的书籍\n- 做笔记和思维导图\n- 定期回顾和总结\n- 与他人分享交流\n\n读书不在多，而在于读懂、读透、能应用。",
        "今天分享一个心态调整的方法：当遇到困难时，试着换个角度看问题。\n\n每个挑战都是成长的机会，每次失败都是学习的过程。保持积极乐观的心态很重要。",
        "最后提醒：本平台所有内容仅为个人分享，不构成任何专业建议。\n\n请大家根据自身情况独立判断，理性决策。如有专业需求，请咨询相关领域的专业人士。",
    ]

    fake_posts = [
        {
            "id": i + 1,
            "content": content,
            "image_path": None,
            "created_at": (base_time - timedelta(hours=len(fake_contents) - i)).isoformat() + 'Z',
        }
        for i, content in enumerate(fake_contents)
    ]

    return fake_posts


def send_security_headers(handler_instance):
    """添加安全响应头"""
    handler_instance.send_header('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
    handler_instance.send_header('X-Frame-Options', 'DENY')
    handler_instance.send_header('X-Content-Type-Options', 'nosniff')
    handler_instance.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
    handler_instance.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), interest-cohort=()')


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析查询参数
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # 验证 limit 参数
        try:
            limit = int(query_params.get('limit', [100])[0])
            limit = min(max(limit, 1), 1000)  # 限制在 1-1000 之间
        except (ValueError, IndexError):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            send_security_headers(self)
            self.end_headers()
            error_response = {
                "success": False,
                "error": "Invalid limit parameter"
            }
            self.wfile.write(json.dumps(error_response).encode())
            return

        try:
            posts = []

            # 如果配置了 Supabase，从数据库获取数据
            if supabase:
                try:
                    logger.info({
                        "event": "supabase_query_start",
                        "table": "gold_signals",
                        "limit": limit,
                    })
                    print("[posts.py] Supabase query start", json.dumps({"table": "gold_signals", "limit": limit}))

                    # 只选择前端需要的字段，不暴露内部字段
                    response = supabase.table('gold_signals') \
                        .select('id, content, image_path, created_at') \
                        .eq('is_filtered', False) \
                        .is_('deleted_at', 'null') \
                        .eq('status', 'published') \
                        .order('created_at', desc=True) \
                        .limit(limit) \
                        .execute()

                    response_data = response.data if response and response.data else []
                    response_error = getattr(response, "error", None)
                    logger.info({
                        "event": "supabase_query_result",
                        "count": len(response_data),
                        "error": response_error,
                    })
                    print("[posts.py] Supabase query result", json.dumps({
                        "count": len(response_data),
                        "error": response_error,
                        "preview": response_data[:2],
                    }, default=str))
                    if response_error:
                        logger.error({"event": "supabase_query_error", "error": response_error})
                        print("[posts.py] Supabase query error", response_error)

                    if response_data:
                        posts = response_data
                except Exception as db_error:
                    logger.error(f"Database query failed: {db_error}")
                    print(f"[posts.py] Database query failed: {db_error}")
                    # 数据库错误时，如果是开发环境则返回假数据，生产环境返回空数组
                    if IS_DEVELOPMENT:
                        posts = get_fake_posts()

            # 如果没有配置 Supabase 且是开发环境，返回假数据
            elif IS_DEVELOPMENT:
                posts = get_fake_posts()

            # 设置响应头
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            send_security_headers(self)
            self.end_headers()

            # 返回 JSON 响应
            response_data = {
                "success": True,
                "count": len(posts),
                "data": posts
            }
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            # 记录错误但不暴露详细信息给客户端
            logger.error(f"Unexpected error in /api/posts: {e}")

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            send_security_headers(self)
            self.end_headers()

            error_response = {
                "success": False,
                "error": "Internal server error"
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        # 处理 CORS 预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        send_security_headers(self)
        self.end_headers()
