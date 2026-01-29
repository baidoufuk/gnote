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
        """处理心跳请求"""
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

            # 获取会话信息
            session_response = supabase.table('user_sessions').select('user_id').eq('id', session_id).single().execute()

            if not session_response.data:
                self.send_error_response(404, '会话不存在')
                return

            user_id = session_response.data['user_id']

            # 更新会话的 last_seen_at
            supabase.table('user_sessions').update({
                'last_seen_at': datetime.utcnow().isoformat()
            }).eq('id', session_id).execute()

            # 检查用户账号状态
            profile_response = supabase.table('user_profiles').select('account_status').eq('user_id', user_id).single().execute()

            if not profile_response.data:
                self.send_error_response(404, '用户不存在')
                return

            account_status = profile_response.data['account_status']

            # 如果账号被封禁，强制登出
            if account_status == 'banned':
                supabase.table('user_sessions').update({
                    'is_active': False
                }).eq('id', session_id).execute()

                self.send_success_response({
                    'force_logout': True,
                    'message': '您的账号已被封禁'
                })
                return

            # 返回成功响应
            self.send_success_response({
                'force_logout': False,
                'account_status': account_status
            })

        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
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