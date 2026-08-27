"""
派友记（PI Life）— 持币等级计算
"""
from config import LEVEL_MAP


def calculate_level(balance: int) -> int:
    """
    根据持币余额计算等级（0~4）
    照搬暖忆录分层权重的设计思路[reference:31]
    """
    for level, info in LEVEL_MAP.items():
        if info["min"] <= balance <= info["max"]:
            return level
    return 0  # 默认青铜


def get_level_info(level: int) -> dict:
    """获取等级详细信息"""
    return LEVEL_MAP.get(level, LEVEL_MAP[0])