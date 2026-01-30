from http.server import BaseHTTPRequestHandler
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """处理修改密码请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            username = data.get('username')
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            # 验证必填字段
            if not username or not old_password or not new_password:
                self.send_error_response(400, '用户名、旧密码和新密码不能为空')
                return

            if len(new_password) < 6:
                self.send_error_response(400, '新密码至少 6 位')
                return

            if old_password == new_password:
                self.send_error_response(400, '新密码不能与旧密码相同')
                return

            if not supabase:
                self.send_error_response(500, 'Supabase 未初始化')
                return

            # 1. 验证旧密码
            email = f"{username}@internal.local"
            try:
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": old_password
                })

                if not auth_response.user:
                    self.send_error_response(401, '旧密码错误')
                    return

                user_id = auth_response.user.id
            except Exception as e:
                logger.error(f"Auth error: {e}")
                self.send_error_response(401, '旧密码错误')
                return

            # 2. 更新密码
            try:
                supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"password": new_password}
                )
            except Exception as e:
                logger.error(f"Update password error: {e}")
                self.send_error_response(500, f'修改密码失败: {str(e)}')
                return

            # 3. 返回成功响应
            self.send_success_response({
                'message': '密码修改成功，请使用新密码重新登录'
            })

        except Exception as e:
            logger.error(f"Change password error: {e}")
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