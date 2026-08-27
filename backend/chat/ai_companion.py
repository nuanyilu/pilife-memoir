"""
AI陪伴对话引擎

来源: 复制永恒版chat逻辑(ai_server_v4.py L188-340)
改造:
  - System Prompt加入PI Life社区语境
  - 角色名待定(派友助手?)
  - 情绪词典加入投资情绪(FUD/FOMO/贪婪/恐惧)
  - 记忆检索加入持仓记忆

三级降级: 混元 → 通义千问 → 底座引擎(复用ai_caller.py)
""")
# TODO
