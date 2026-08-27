"""
社区路由

来源: 复制永恒版square全套
改造: 加官方公告频道

接口:
  GET/POST /api/v1/square/posts        帖子列表/发帖
  GET      /api/v1/square/posts/<id>   帖子详情
  POST     /api/v1/square/posts/<id>/like     点赞
  POST     /api/v1/square/posts/<id>/comments 评论
  GET      /api/v1/square/topics       话题列表
  GET      /api/v1/square/feed         热度Feed
  GET/POST /api/v1/announcements       官方公告【新建】
""")
# TODO: Blueprint定义 + 路由实现

