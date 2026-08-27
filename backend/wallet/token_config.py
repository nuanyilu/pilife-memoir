"""
派友记（PI Life）— PI Life 合约配置
"""
from config import PI_CONTRACT_ADDRESS

# 合约地址（主网部署后替换）
CONTRACT_ADDRESS = PI_CONTRACT_ADDRESS

# 最小 ABI（仅 balanceOf，用于查询余额）
MOCK_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]