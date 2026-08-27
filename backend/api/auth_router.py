"""
认证路由

来源: 复制永恒版auth模块
改造: 加钱包签名登录

接口:
  POST /api/v1/auth/register      邮箱注册
  POST /api/v1/auth/login         邮箱登录
  POST /api/v1/auth/login_guest   访客登录
  POST /api/v1/auth/login_wallet  钱包签名登录【新建】
  GET  /api/v1/auth/me            获取当前用户
  PUT  /api/v1/auth/me            更新用户信息
""")
# TODO: Blueprint定义 + 路由实现

