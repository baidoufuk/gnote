from http.server import BaseHTTPRequestHandler
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")
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
        """处理管理员重置密码请求"""
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
            new_password = data.get('new_password')

            # 验证必填字段
            if not username or not new_password:
                self.send_error_response(400, '用户名和新密码不能为空')
                return

            if len(new_password) < 6:
                self.send_error_response(400, '新密码至少 6 位')
                return

            if not supabase:
                self.send_error_response(500, 'Supabase 未初始化')
                return

            # 1. 查找用户
            try:
                profile_response = supabase.table('user_profiles').select('user_id').eq('username', username).single().execute()

                if not profile_response.data:
                    self.send_error_response(404, '用户不存在')
                    return

                user_id = profile_response.data['user_id']
            except Exception as e:
                logger.error(f"Find user error: {e}")
                self.send_error_response(404, '用户不存在')
                return

            # 2. 重置密码
            try:
                supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"password": new_password}
                )
            except Exception as e:
                logger.error(f"Reset password error: {e}")
                self.send_error_response(500, f'重置密码失败: {str(e)}')
                return

            # 3. 返回成功响应
            self.send_success_response({
                'username': username,
                'message': '密码重置成功'
            })

        except Exception as e:
            logger.error(f"Reset password error: {e}")
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