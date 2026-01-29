from http.server import BaseHTTPRequestHandler
import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 配置
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")

# CORS 配置（默认允许所有来源，生产环境应设置为具体域名）
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# 初始化 Supabase 客户端
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")


def send_security_headers(handler_instance):
    """添加安全响应头"""
    handler_instance.send_header('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
    handler_instance.send_header('X-Frame-Options', 'DENY')
    handler_instance.send_header('X-Content-Type-Options', 'nosniff')
    handler_instance.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
    handler_instance.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), interest-cohort=()')


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 验证 Telegram Webhook Secret（必须配置）
            if not TELEGRAM_WEBHOOK_SECRET:
                logger.error("TELEGRAM_WEBHOOK_SECRET not configured")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                send_security_headers(self)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Server misconfigured"}).encode())
                return

            secret_token = self.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
            if secret_token != TELEGRAM_WEBHOOK_SECRET:
                logger.warning(f"Invalid webhook secret token attempt")
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                send_security_headers(self)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Forbidden"}).encode())
                return

            # 限制请求体大小（最大 1MB）
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 1024 * 1024:  # 1MB
                self.send_response(413)
                self.send_header('Content-type', 'application/json')
                send_security_headers(self)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Payload too large"}).encode())
                return

            # 读取请求体
            body = self.rfile.read(content_length)

            # 验证 JSON 格式
            try:
                update_data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                send_security_headers(self)
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Invalid JSON"}).encode())
                return

            # 处理 Telegram 消息
            # 注意：这里简化了处理逻辑，实际应该包含完整的 Bot 处理逻辑
            # 由于 Vercel Serverless 的限制，复杂的 Bot 逻辑可能需要单独部署

            # 提取消息内容
            message = update_data.get('message', {})
            text = message.get('text', '')

            logger.info(f"Received Telegram update: {update_data.get('update_id')}")

            # 如果有 Supabase 连接，可以保存消息
            if supabase and text:
                # 这里可以添加保存到数据库的逻辑
                # 例如：supabase.table('gold_signals').insert({...}).execute()
                pass

            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            send_security_headers(self)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

        except Exception as e:
            # 记录错误但不暴露详细信息
            logger.error(f"Unexpected error in webhook: {e}")

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            send_security_headers(self)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Internal server error"}).encode())

    def do_OPTIONS(self):
        # 处理 CORS 预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        send_security_headers(self)
        self.end_headers()
