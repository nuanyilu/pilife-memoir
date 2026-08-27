from flask import Flask, jsonify
from flask_cors import CORS
from db.database import init_db
from api.auth_router import auth_bp

app = Flask(__name__)
CORS(app)

# 注册蓝图
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # 启动前初始化数据库
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)