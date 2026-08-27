import hashlib
import secrets
import time
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify

from config import JWT_SECRET
from db.models import (
    get_user_by_email, get_user_by_wallet, create_user,
    create_guest_user, update_user_level, update_user_balance,
    get_user_by_id
)
from wallet.connector import verify_signature
from wallet.chain_reader import get_pi_balance
from wallet.level_system import calculate_level

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# ===== JWT 辅助函数 =====
def generate_token(user_id, email=None, wallet=None):
    """生成JWT token，7天过期"""
    payload = {
        'user_id': user_id,
        'email': email,
        'wallet': wallet,
        'exp': int(time.time()) + 7 * 24 * 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """验证JWT token，返回payload或None"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None

def require_jwt(f):
    """
    照搬暖忆录 require_jwt 装饰器风格
    从请求头获取 Authorization: Bearer <token>
    验证后将 user_id 存入 request.current_user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': '未提供认证令牌'}), 401
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'error': '无效或过期的令牌'}), 401
        request.current_user = {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'wallet': payload.get('wallet')
        }
        return f(*args, **kwargs)
    return decorated

# ===== 密码辅助 =====
def hash_password(password):
    salt = secrets.token_hex(8)
    return salt + ':' + hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(stored, password):
    if not stored or ':' not in stored:
        return False
    salt, h = stored.split(':', 1)
    return h == hashlib.sha256((salt + password).encode()).hexdigest()

# ===== 路由 =====
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname', '派友用户')
    if not email or not password:
        return jsonify({'success': False, 'error': '邮箱和密码必填'}), 400
    if get_user_by_email(email):
        return jsonify({'success': False, 'error': '邮箱已被注册'}), 400
    pwd_hash = hash_password(password)
    user_id = create_user(email, pwd_hash, nickname, login_type='email')
    token = generate_token(user_id, email=email)
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'email': email,
            'nickname': nickname,
            'token': token
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'success': False, 'error': '邮箱和密码必填'}), 400
    user = get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    if not verify_password(user['password_hash'], password):
        return jsonify({'success': False, 'error': '密码错误'}), 401
    token = generate_token(user['id'], email=email, wallet=user.get('wallet_address'))
    return jsonify({
        'success': True,
        'data': {
            'user_id': user['id'],
            'email': email,
            'nickname': user['nickname'],
            'wallet': user.get('wallet_address'),
            'balance': user.get('pi_balance', 0),
            'level': user.get('pi_level', 0),
            'token': token
        }
    })

@auth_bp.route('/wallet/login', methods=['POST'])
def wallet_login():
    data = request.get_json()
    address = data.get('address')
    signature = data.get('signature')
    message = data.get('message', 'Login to Paiyouji')
    if not address or not signature:
        return jsonify({'success': False, 'error': '缺少钱包地址或签名'}), 400
    if not verify_signature(address, message, signature):
        return jsonify({'success': False, 'error': '签名验证失败'}), 401

    user = get_user_by_wallet(address)
    if not user:
        nickname = f'钱包_{address[-6:]}'
        user_id = create_user(
            email=None,
            password_hash=None,
            nickname=nickname,
            login_type='wallet',
            wallet_address=address
        )
        user = get_user_by_id(user_id)
    else:
        user_id = user['id']

    balance = get_pi_balance(address)
    level = calculate_level(balance)
    update_user_balance(user_id, balance)
    update_user_level(user_id, level)

    token = generate_token(user_id, wallet=address)
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'nickname': user['nickname'],
            'wallet': address,
            'balance': balance,
            'level': level,
            'token': token
        }
    })

@auth_bp.route('/guest', methods=['POST'])
def guest_login():
    user_id = create_guest_user()
    user = get_user_by_id(user_id)
    token = generate_token(user_id)
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'nickname': user['nickname'],
            'token': token,
            'is_guest': True
        }
    })

@auth_bp.route('/me', methods=['GET'])
@require_jwt
def me():
    user_id = request.current_user['user_id']
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    return jsonify({
        'success': True,
        'data': {
            'user_id': user['id'],
            'email': user['email'],
            'nickname': user['nickname'],
            'avatar': user['avatar'],
            'wallet': user['wallet_address'],
            'balance': user['pi_balance'],
            'level': user['pi_level'],
            'created_at': user['created_at']
        }
    })