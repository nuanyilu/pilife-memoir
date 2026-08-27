# 派友记 — PI Life社区社交DApp

基于暖忆录永恒版(完整版) + warm_memoir(AI日记引擎) 开发。

## 技术栈
- 后端: Python 3.11 + Flask + flask-socketio + SQLite(WAL)
- 前端: uni-app H5
- AI: 混元 → 通义千问 → 底座引擎(三级降级)
- 链: BSC (web3.py)

## 快速启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

## 开发阶段
- BSC RPC: https://bsc-dataseed.binance.org
- 合约地址: 0x0000000000000000000000000000000000000000 (占位)
- Mock模式: chain_reader返回假数据, connector跳过签名验证
