"""
派友记（PI Life）— 全局配置文件
照搬暖忆录 config 风格：环境变量优先，硬编码兜底
"""
import os
from pathlib import Path

# ===== 路径 =====
BASE_DIR = Path(__file__).parent.parent
DB_PATH = os.path.join(BASE_DIR, "paiyouji.db")

# ===== JWT（照搬暖忆录 make_jwt/verify_jwt 的密钥设计）=====
JWT_SECRET = os.environ.get("JWT_SECRET", "paiyouji_secret_2026")

# ===== AI 调用（三级降级，照搬 ai_caller.py 风格）=====
# 主用：DeepSeek（对标暖忆录的混元）
AI_API_URL = os.environ.get("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
AI_API_KEY = os.environ.get("AI_API_KEY", "")

# 降级1：备用接口（对标暖忆录的通义千问）
AI_FALLBACK_URL = os.environ.get("AI_FALLBACK_URL", "")
AI_FALLBACK_KEY = os.environ.get("AI_FALLBACK_KEY", "")

# 降级2：本地底座（对标暖忆录的 BASE_ENGINE）
BASE_ENGINE_URL = os.environ.get("BASE_ENGINE_URL", "http://localhost:6335")

# Mock 模式（开发期使用）
AI_MOCK = os.environ.get("AI_MOCK", "true") == "true"

# ===== BSC 链上配置 =====
BSC_RPC = os.environ.get("BSC_RPC", "https://bsc-dataseed.binance.org")
PI_CONTRACT_ADDRESS = os.environ.get(
    "PI_CONTRACT_ADDRESS",
    "0x0000000000000000000000000000000000000000"  # 占位，主网上线后替换
)

# Mock 模式（跳过签名验证，返回假余额）
WALLET_MOCK = os.environ.get("WALLET_MOCK", "true") == "true"

# ===== 持币等级映射（新增，暖忆录无此模块）=====
LEVEL_MAP = {
    0: {"name": "青铜", "min": 0, "max": 99},
    1: {"name": "白银", "min": 100, "max": 999},
    2: {"name": "黄金", "min": 1000, "max": 9999},
    3: {"name": "钻石", "min": 10000, "max": 99999},
    4: {"name": "传奇", "min": 100000, "max": float("inf")},
}