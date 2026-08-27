"""
派友记（PI Life）— 钱包签名验证
"""
from config import WALLET_MOCK


def verify_signature(address: str, message: str, signature: str) -> bool:
    """
    验证钱包签名
    Mock 模式直接返回 True（开发期使用）
    生产模式使用 eth_account 恢复签名地址
    """
    if WALLET_MOCK:
        return True

    # 生产模式：使用 eth_account 验证
    try:
        from eth_account.messages import encode_defunct
        from eth_account import Account

        msg = encode_defunct(text=message)
        recovered = Account.recover_message(msg, signature=signature)
        return recovered.lower() == address.lower()
    except Exception:
        return False