from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase 配置
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or os.environ.get("SUPABASE_KEY", "")

# CORS 配置
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# 初始化 Supabase 客户端
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
else:
    logger.warning("Supabase env vars missing")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """处理登出请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            session_id = data.get('session_id')

            if not session_id:
                self.send_error_response(400, '会话ID不能为空')
                return

            # 检查 Supabase 客户端
            if not supabase:
                self.send_error_response(500, 'Supabase 未初始化')
                return

            # 更新会话状态
            supabase.table('user_sessions').update({
                'is_active': False,
                'last_seen_at': datetime.utcnow().isoformat()
            }).eq('id', session_id).execute()

            # 返回成功响应
            self.send_success_response({'message': '登出成功'})

        except Exception as e:
            logger.error(f"Logout error: {e}")
            self.send_error_response(500, f'服务器错误: {str(e)}')

    def send_success_response(self, data):
        """发送成功响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'data': data
        }).encode('utf-8'))

    def send_error_response(self, status_code, error_message):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'error': error_message
        }).encode('utf-8'))