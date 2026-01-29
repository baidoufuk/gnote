from http.server import BaseHTTPRequestHandler
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


def calculate_fingerprint_similarity(fp1, fp2):
    """
    计算两个设备指纹的相似度（加权）
    返回 0-1 之间的相似度分数
    """
    if not fp1 or not fp2:
        return 0.0

    weights = {
        'canvas_hash': 0.3,
        'audio_hash': 0.2,
        'screen_width': 0.1,
        'screen_height': 0.1,
        'device_pixel_ratio': 0.05,
        'platform': 0.1,
        'browser_family': 0.05,
        'browser_major': 0.05,
        'timezone_offset': 0.05
    }

    total_score = 0.0
    total_weight = 0.0

    for key, weight in weights.items():
        if key in fp1 and key in fp2:
            total_weight += weight
            if fp1[key] == fp2[key]:
                total_score += weight

    return total_score / total_weight if total_weight > 0 else 0.0


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """处理登录请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            username = data.get('username')
            password = data.get('password')
            fingerprint_raw = data.get('fingerprint_raw')
            fingerprint_hash = data.get('fingerprint_hash')

            # 验证必填字段
            if not username or not password:
                self.send_error_response(400, '用户名和密码不能为空')
                return

            if not fingerprint_raw or not fingerprint_hash:
                self.send_error_response(400, '设备指纹信息缺失')
                return

            # 检查 Supabase 客户端
            if not supabase:
                self.send_error_response(500, 'Supabase 未初始化')
                return

            # 1. 使用 Supabase Auth 登录
            try:
                # 构造邮箱（username@internal.local）
                email = f"{username}@internal.local"
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if not auth_response.user:
                    self.send_error_response(401, '用户名或密码错误')
                    return

                user_id = auth_response.user.id
            except Exception as e:
                logger.error(f"Auth error: {e}")
                self.send_error_response(401, '用户名或密码错误')
                return

            # 2. 获取用户资料
            profile_response = supabase.table('user_profiles').select('*').eq('user_id', user_id).single().execute()

            if not profile_response.data:
                self.send_error_response(404, '用户资料不存在')
                return

            profile = profile_response.data

            # 3. 检查账号状态
            if profile['account_status'] == 'banned':
                self.send_error_response(403, '您的账号已被封禁，无法登录')
                return

            # 4. 查询活跃会话（15分钟内）
            fifteen_min_ago = (datetime.utcnow() - timedelta(minutes=15)).isoformat()
            active_sessions_response = supabase.table('user_sessions').select('*').eq('user_id', user_id).eq('is_active', True).gte('last_seen_at', fifteen_min_ago).execute()

            active_sessions = active_sessions_response.data or []

            # 5. 处理并发会话
            risk_score_change = 0
            similarity_score = 1.0

            if active_sessions:
                # 有活跃会话，计算指纹相似度
                old_session = active_sessions[0]
                old_fingerprint = old_session.get('fingerprint_raw', {})

                similarity_score = calculate_fingerprint_similarity(old_fingerprint, fingerprint_raw)

                if similarity_score < 0.5:
                    # 指纹不相似，可能是账号共享
                    risk_score_change = 15

                    # 记录异常日志
                    supabase.table('account_anomaly_logs').insert({
                        'user_id': user_id,
                        'event_type': 'concurrent_login_different_device',
                        'details': {
                            'old_fingerprint_hash': old_session.get('fingerprint_hash'),
                            'new_fingerprint_hash': fingerprint_hash,
                            'similarity_score': similarity_score
                        },
                        'risk_score_change': risk_score_change
                    }).execute()

                # 踢掉旧会话
                supabase.table('user_sessions').update({
                    'is_active': False,
                    'kicked_reason': 'new_login'
                }).eq('id', old_session['id']).execute()

            # 6. 创建新会话
            new_session_response = supabase.table('user_sessions').insert({
                'user_id': user_id,
                'fingerprint_raw': fingerprint_raw,
                'fingerprint_hash': fingerprint_hash,
                'ip_address': self.headers.get('X-Forwarded-For', self.client_address[0]),
                'user_agent': self.headers.get('User-Agent', ''),
                'is_active': True,
                'similarity_score': similarity_score
            }).execute()

            new_session = new_session_response.data[0] if new_session_response.data else None

            if not new_session:
                self.send_error_response(500, '创建会话失败')
                return

            # 7. 更新用户资料
            new_risk_score = profile['risk_score'] + risk_score_change
            new_account_status = profile['account_status']

            # 根据风险分数调整账号状态
            if new_risk_score >= 70:
                new_account_status = 'banned'
            elif new_risk_score >= 40:
                new_account_status = 'limited'
            else:
                new_account_status = 'active'

            supabase.table('user_profiles').update({
                'last_login_at': datetime.utcnow().isoformat(),
                'risk_score': new_risk_score,
                'account_status': new_account_status,
                'status_updated_at': datetime.utcnow().isoformat() if new_account_status != profile['account_status'] else profile.get('status_updated_at')
            }).eq('user_id', user_id).execute()

            # 8. 返回成功响应
            self.send_success_response({
                'user': {
                    'id': user_id,
                    'username': profile['username'],
                    'account_status': new_account_status,
                    'risk_score': new_risk_score
                },
                'session': {
                    'id': new_session['id'],
                    'created_at': new_session['created_at']
                }
            })

        except Exception as e:
            logger.error(f"Login error: {e}")
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
