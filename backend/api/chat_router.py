"""
聊天路由

来源: 复制永恒版chat + 新建群聊
改造: prompt加入PI Life社区语境

接口:
  POST /api/v1/chat               AI陪伴对话
  GET  /api/v1/chat/history       聊天历史
  GET  /api/v1/chat/rooms         群聊房间列表
  POST /api/v1/chat/rooms         创建群聊房间
  POST /api/v1/chat/rooms/<id>/join  加入房间
""")
# TODO: Blueprint定义 + 路由实现 + WebSocket事件

