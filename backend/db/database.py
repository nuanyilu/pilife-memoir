"""
派友记（PI Life）— 数据库层
照搬暖忆录 db.py 风格：sqlite3.Row + get_db() + init_db() 集中建表
"""
import sqlite3
import os
from config import DB_PATH


def get_db():
    """照搬暖忆录 get_db()：每次返回新的 Row 工厂连接，开启 WAL 模式[reference:15]"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """照搬暖忆录 init_db()：集中建表 + 索引[reference:16]"""
    conn = get_db()
    c = conn.cursor()

    # ===== 1. 用户表（扩展自暖忆录 users）=====
    # 暖忆录原字段：id, email, password_hash, nickname, avatar, login_type, created_at, last_login[reference:17]
    # 派友记扩展：wallet_address, pi_balance, pi_level
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            nickname TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            login_type TEXT DEFAULT 'email',
            wallet_address TEXT UNIQUE,
            pi_balance INTEGER DEFAULT 0,
            pi_level INTEGER DEFAULT 0,
            created_at TEXT,
            last_login TEXT
        )
    """)

    # ===== 2. 用户画像/事实（照搬暖忆录 user_facts）[reference:18]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            fact_type TEXT NOT NULL DEFAULT 'other',
            fact_value TEXT NOT NULL DEFAULT '',
            fact_layer TEXT DEFAULT 'identity',
            display_name TEXT DEFAULT '',
            source TEXT DEFAULT 'user',
            confidence REAL DEFAULT 1.0,
            weight INTEGER DEFAULT 10,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_facts_uid ON user_facts(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON user_facts(user_id, fact_type)")

    # ===== 3. 聊天记录（照搬暖忆录 chat_messages）[reference:19]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            content TEXT NOT NULL DEFAULT '',
            emotion TEXT DEFAULT '',
            created_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_chat_uid ON chat_messages(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_chat_time ON chat_messages(user_id, created_at)")

    # ===== 4. 日记（照搬暖忆录 diaries）[reference:20]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            content TEXT DEFAULT '',
            mood TEXT DEFAULT '平静',
            weather TEXT DEFAULT '',
            is_auto INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_diary_uid ON diaries(user_id)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_diary_date ON diaries(user_id, date)")

    # ===== 5. 积分/PI代币（改造自暖忆录 points + point_logs）=====
    # 暖忆录原表：points(user_id, balance, updated_at)[reference:21]
    # 派友记改为 pi_tokens，增加 total_earned 字段
    c.execute("""
        CREATE TABLE IF NOT EXISTS pi_tokens (
            user_id TEXT PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)
    # 暖忆录原表：point_logs(id, user_id, amount, reason, scene, created_at)[reference:22]
    c.execute("""
        CREATE TABLE IF NOT EXISTS pi_token_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            reason TEXT DEFAULT '',
            scene TEXT DEFAULT '',
            created_at TEXT
        )
    """)

    # ===== 6. 社区帖子（照搬暖忆录 square_posts）[reference:23]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS square_posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion_tag TEXT DEFAULT '',
            topic TEXT DEFAULT '',
            images TEXT DEFAULT '[]',
            likes INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            anonymous INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # ===== 7. 社区评论（照搬暖忆录 square_comments）[reference:24]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS square_comments (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # ===== 8. 社区点赞（照搬暖忆录 square_likes）[reference:25]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS square_likes (
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            PRIMARY KEY (post_id, user_id)
        )
    """)

    # ===== 9. 社区话题（照搬暖忆录 square_topics）[reference:26]=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS square_topics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            post_count INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # ===== 10. 群聊房间（新增，暖忆录无此表）=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            owner_id TEXT NOT NULL,
            is_public INTEGER DEFAULT 1,
            member_count INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # ===== 11. 群聊成员（新增）=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_room_members (
            room_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            joined_at TEXT,
            PRIMARY KEY (room_id, user_id)
        )
    """)

    # ===== 12. 官方公告（新增）=====
    c.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()