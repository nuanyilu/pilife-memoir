"""
派友记（PI Life）— 数据模型辅助函数
照搬暖忆录风格：直接用 sqlite3 原生 SQL，不引入 ORM
"""
import hashlib
import time
from db.database import get_db


def generate_user_id():
    """照搬暖忆录 user_id 生成方式：user_{md5}[reference:27]"""
    return f"user_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"


def get_user_by_id(user_id):
    """根据 user_id 查用户"""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def get_user_by_email(email):
    """根据 email 查用户"""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def get_user_by_wallet(wallet_address):
    """根据钱包地址查用户"""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE wallet_address = ?", (wallet_address,)).fetchone()
    conn.close()
    return row


def create_user(email, password_hash, nickname="派友用户", login_type="email", wallet_address=None):
    """创建用户，照搬暖忆录 auth_register 逻辑[reference:28]"""
    uid = generate_user_id()
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    conn = get_db()
    conn.execute(
        "INSERT INTO users (id, email, password_hash, nickname, login_type, wallet_address, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uid, email, password_hash, nickname, login_type, wallet_address, now, now)
    )
    # 初始化 PI 代币（照搬暖忆录初始化积分的逻辑[reference:29]）
    conn.execute(
        "INSERT OR IGNORE INTO pi_tokens (user_id, balance, total_earned, updated_at) VALUES (?, ?, ?, ?)",
        (uid, 0, 0, now)
    )
    conn.commit()
    conn.close()
    return uid


def create_guest_user():
    """创建访客用户，照搬暖忆录 auth_guest 逻辑[reference:30]"""
    uid = f"guest_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    conn = get_db()
    conn.execute(
        "INSERT INTO users (id, nickname, login_type, created_at, last_login) VALUES (?, ?, ?, ?, ?)",
        (uid, "访客", "guest", now, now)
    )
    conn.execute(
        "INSERT OR IGNORE INTO pi_tokens (user_id, balance, total_earned, updated_at) VALUES (?, ?, ?, ?)",
        (uid, 0, 0, now)
    )
    conn.commit()
    conn.close()
    return uid


def update_user_level(user_id, level):
    """更新用户等级"""
    conn = get_db()
    conn.execute("UPDATE users SET pi_level = ? WHERE id = ?", (level, user_id))
    conn.commit()
    conn.close()


def update_user_balance(user_id, balance):
    """更新用户持币余额"""
    conn = get_db()
    conn.execute("UPDATE users SET pi_balance = ? WHERE id = ?", (balance, user_id))
    conn.execute(
        "UPDATE pi_tokens SET balance = ?, updated_at = ? WHERE user_id = ?",
        (balance, time.strftime("%Y-%m-%dT%H:%M:%S"), user_id)
    )
    conn.commit()
    conn.close()