"""
暖忆录·永恒版 API — 数据库初始化
所有SQLite表集中定义，方便后续模块使用
"""
import sqlite3, os, uuid, time, hashlib
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "nuan.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # 1. 用户表（替代微信OpenID → 邮箱/密码 + JWT）
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        nickname TEXT DEFAULT '',
        avatar TEXT DEFAULT '',
        login_type TEXT DEFAULT 'email',
        created_at TEXT,
        last_login TEXT
    )""")
    
    # 2. 用户画像/偏好（替代小程序 user_facts 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS user_facts (
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
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_facts_uid ON user_facts(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON user_facts(user_id, fact_type)")
    
    # 3. 聊天记录（替代小程序 personal_chat_messages 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        content TEXT NOT NULL DEFAULT '',
        emotion TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_chat_uid ON chat_messages(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_chat_time ON chat_messages(user_id, created_at)")
    
    # 4. 日记（替代小程序 diaries 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS diaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        content TEXT DEFAULT '',
        mood TEXT DEFAULT '平静',
        weather TEXT DEFAULT '',
        is_auto INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_diary_uid ON diaries(user_id)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_diary_date ON diaries(user_id, date)")
    
    # 5. 温暖瞬间（替代小程序 warm_moments 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS warm_moments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        summary TEXT DEFAULT '',
        comment TEXT DEFAULT '',
        original_text TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_warm_uid ON warm_moments(user_id)")
    
    # 6. 提醒（替代小程序 user_reminders 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'general',
        due_date TEXT,
        due_time TEXT DEFAULT '',
        priority TEXT DEFAULT 'normal',
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        updated_at TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_reminder_uid ON reminders(user_id)")
    
    # 7. 月度回顾（替代小程序 monthly_reviews 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS monthly_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        month TEXT NOT NULL,
        content TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_review ON monthly_reviews(user_id, month)")
    
    # 8. 每日画像（替代小程序 user_daily_profile 集合）
    c.execute("""CREATE TABLE IF NOT EXISTS daily_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        mood TEXT DEFAULT '',
        summary TEXT DEFAULT '',
        keywords TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_profile ON daily_profile(user_id, date)")
    
    # 9. 用户每周回顾
    c.execute("""CREATE TABLE IF NOT EXISTS weekly_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        week_start TEXT NOT NULL,
        content TEXT DEFAULT '',
        is_read INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly ON weekly_reviews(user_id, week_start)")
    
    # 10. 积分/暖币（替代小程序 user_points + point_logs）
    c.execute("""CREATE TABLE IF NOT EXISTS points (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        updated_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS point_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        reason TEXT DEFAULT '',
        scene TEXT DEFAULT '',
        created_at TEXT
    )""")
    
    # 11. 会话缓存（替代小程序 chat_session_cache）
    c.execute("""CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        context_summary TEXT DEFAULT '',
        message_count INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        expire_at TEXT,
        created_at TEXT,
        updated_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS session_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT DEFAULT '',
        tokens INTEGER DEFAULT 0,
        importance REAL DEFAULT 0.5,
        created_at TEXT
    )""")
    
    # 12. 家庭（替代小程序 family_groups）
    c.execute("""CREATE TABLE IF NOT EXISTS families (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        member_count INTEGER DEFAULT 1,
        invite_code TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS family_members (
        family_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT DEFAULT 'member',
        joined_at TEXT,
        PRIMARY KEY (family_id, user_id)
    )""")
    
    # 13. 回响谷（square.db迁移过来）
    c.execute("""CREATE TABLE IF NOT EXISTS square_posts (
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
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS square_comments (
        id TEXT PRIMARY KEY,
        post_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS square_likes (
        post_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        PRIMARY KEY (post_id, user_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS square_topics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT '',
        post_count INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    
    # 14. 纪念日/重要日期
    c.execute("""CREATE TABLE IF NOT EXISTS anniversaries (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        type TEXT DEFAULT 'birthday',
        remind_days INTEGER DEFAULT 7,
        created_at TEXT
    )""")
    
    # 15. 人生事件
    c.execute("""CREATE TABLE IF NOT EXISTS life_events (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        year TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        event_type TEXT DEFAULT 'milestone',
        created_at TEXT
    )""")
    
    conn.commit()
    conn.close()
    return True

def ensure_default_user():
    """确保有默认用户（避免匿名无法用功能）"""
    conn = get_db()
    existing = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    if not existing:
        from werkzeug.security import generate_password_hash
        uid = f"user_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
        now = datetime.now().isoformat()
        conn.execute("INSERT INTO users (id,email,password_hash,nickname,login_type,created_at,last_login) VALUES (?,?,?,?,?,?,?)",
                     (uid, "admin@nuan.com", generate_password_hash("nuan2026"), "庄主", "email", now, now))
        # 给默认用户积分
        conn.execute("INSERT OR IGNORE INTO points (user_id, balance, updated_at) VALUES (?, ?, ?)", (uid, 100, now))
        conn.commit()
        print(f"✅ 创建默认用户: {uid}")
    conn.close()

if __name__ == "__main__":
    init_db()
    ensure_default_user()
    print("✅ 数据库初始化完成")
