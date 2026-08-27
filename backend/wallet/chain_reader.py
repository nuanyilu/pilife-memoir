"""
派友记（PI Life）— BSC 链上查询
"""
import random
from config import BSC_RPC, WALLET_MOCK
from wallet.token_config import CONTRACT_ADDRESS, MOCK_ABI


def get_pi_balance(address: str) -> int:
    """
    查询用户 PI Life 持币余额
    Mock 模式返回随机整数（0 ~ 100000），模拟不同持币等级
    """
    if WALLET_MOCK:
        # 返回随机余额，覆盖青铜到传奇各等级
        return random.randint(0, 100000)

    # 生产模式：使用 web3.py 查询链上余额
    try:
        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(BSC_RPC))
        if not w3.is_connected():
            return 0

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=MOCK_ABI
        )
        balance = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return balance  # 单位：wei，后续可转换为 PI
    except Exception:
        return 0