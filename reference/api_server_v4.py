"""
暖忆录·永恒版 API v4.0 — 完整功能版
逐模块翻译自小程序完整版(miniprogram-6)核心功能
"""
from flask import Flask, request, jsonify, send_from_directory
import requests, time, hashlib, hmac, json, os, re, uuid, sqlite3
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

BASE_ENGINE = "http://61.150.123.162:6335"
DIARY_ENGINE = "http://61.150.123.162:18080"
QDRANT_URL = "http://61.150.123.162:6333"
JWT_SECRET = "nuan_yongheng_secret_2026"
API_PORT = 6337

app = Flask(__name__)
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 修改index.html title
_INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist/index.html")
if os.path.exists(_INDEX_PATH):
    _idx_content = open(_INDEX_PATH, 'r', encoding='utf-8').read()
    if '<title>frontend</title>' in _idx_content:
        open(_INDEX_PATH, 'w', encoding='utf-8').write(_idx_content.replace('<title>frontend</title>', '<title>暖忆录·永恒版</title>'))

# ===== 导入模块 =====
from db import get_db, init_db, DB_PATH
from ai_caller import call_ai, call_hunyuan, call_dashscope, call_ai_with_system
from ai_caller import get_time_period, get_season, get_season_text, get_current_term, format_datetime

# ===== JWT =====
def make_jwt(user_id, login_type="email"):
    import base64 as b64
    def b(data): return b64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()
    h = b({"alg":"HS256","typ":"JWT"})
    p = b({"user_id":user_id,"login_type":login_type,"iat":int(time.time()),"exp":int(time.time())+86400*7})
    sig = hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), "sha256").hexdigest()
    return f"{h}.{p}.{sig}"

def verify_jwt(token):
    import base64 as b64
    try:
        parts = token.split("."); h,p,sig = parts[0],parts[1],parts[2]
        if hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), "sha256").hexdigest() != sig: return None
        payload = json.loads(b64.urlsafe_b64decode(p + "=="))
        return payload if payload.get("exp",0) >= time.time() else None
    except: return None

def require_jwt(f):
    def wrapper(*args,**kwargs):
        auth = request.headers.get("Authorization","")
        user=None; login_type="anonymous"
        if auth.startswith("Bearer "):
            payload = verify_jwt(auth[7:])
            if payload:
                user=payload.get("user_id"); login_type=payload.get("login_type","email")
        request.current_user = user or "anonymous"; request.login_type = login_type
        return f(*args,**kwargs)
    wrapper.__name__=f.__name__; return wrapper

# ===== SPA路由 =====
@app.route("/", defaults={"fallback": None})
@app.route("/<path:fallback>")
def index(fallback):
    return _serve_spa(fallback)

@app.errorhandler(404)
def not_found(e):
    path = request.path
    if path.startswith("/api/"):
        return jsonify({"success":False,"error":"Not found"}),404
    return _serve_spa(path.lstrip("/"))

def _serve_spa(fallback):
    if fallback and ("." in fallback):
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist", fallback)
        if os.path.exists(fpath):
            return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist"), fallback)
    idx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist/index.html")
    if os.path.exists(idx_path):
        with open(idx_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    return jsonify({"success":False,"error":"前端未构建"}),404

# ===== 健康检查 =====
@app.route("/api/v1/health")
def health():
    b=d=q=False
    try: b=requests.get(f"{BASE_ENGINE}/health",timeout=3).json().get("status")=="running"
    except: pass
    try: d=requests.get(f"{DIARY_ENGINE}/",timeout=3).status_code==200
    except: pass
    try: q=requests.get(f"{QDRANT_URL}/",timeout=3).status_code==200
    except: pass
    return jsonify({
        "service":"暖忆录·永恒版 API","version":"4.0",
        "engines":{"base":"✅"if b else"❌","diary":"✅"if d else"❌","qdrant":"✅"if q else"❌"},
        "endpoints":["auth","chat","memory","diary","facts","emotion_sign","heart_fortune","dream","reminder","review","square","family","pi","user","life"]
    })

# ===== 用户认证 =====
@app.route("/api/v1/auth/register", methods=["POST"])
def auth_register():
    data=request.get_json(silent=True) or {}
    email=data.get("email","").strip().lower()
    password=data.get("password","").strip()
    nickname=data.get("nickname","").strip() or "暖忆录用户"
    if not email or not password:
        return jsonify({"success":False,"error":"缺少邮箱或密码"}),400
    if len(password)<6:
        return jsonify({"success":False,"error":"密码至少6位"}),400
    conn=get_db()
    existing=conn.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success":False,"error":"该邮箱已注册"}),409
    uid=f"user_{hashlib.md5(f'{email}_{time.time()}'.encode()).hexdigest()[:12]}"
    pw_hash=generate_password_hash(password)
    now=datetime.now().isoformat()
    conn.execute("INSERT INTO users (id,email,password_hash,nickname,login_type,created_at,last_login) VALUES (?,?,?,?,?,?,?)",
                 (uid,email,pw_hash,nickname,"email",now,now))
    conn.execute("INSERT OR IGNORE INTO points (user_id,balance,updated_at) VALUES (?,?,?)",(uid,100,now))
    conn.commit(); conn.close()
    token=make_jwt(uid,"email")
    return jsonify({"success":True,"token":token,"user":{"id":uid,"email":email,"nickname":nickname,"coins":100}})

@app.route("/api/v1/auth/login", methods=["POST"])
def auth_login():
    data=request.get_json(silent=True) or {}
    email=data.get("email","").strip().lower()
    password=data.get("password","").strip()
    login_type=data.get("login_type","email")
    if login_type=="guest":
        uid=f"guest_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
        token=make_jwt(uid,"guest")
        return jsonify({"success":True,"token":token,"user":{"id":uid,"nickname":"访客","login_type":"guest","is_new":True}})
    if not email or not password:
        return jsonify({"success":False,"error":"缺少邮箱或密码"}),400
    conn=get_db()
    row=conn.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"],password):
        conn.close()
        return jsonify({"success":False,"error":"邮箱或密码错误"}),401
    now=datetime.now().isoformat()
    conn.execute("UPDATE users SET last_login=? WHERE id=?",(now,row["id"]))
    conn.commit(); conn.close()
    token=make_jwt(row["id"],"email")
    return jsonify({"success":True,"token":token,"user":{"id":row["id"],"email":row["email"],"nickname":row["nickname"]}})

@app.route("/api/v1/auth/me", methods=["GET"])
@require_jwt
def auth_me():
    conn=get_db()
    row=conn.execute("SELECT * FROM users WHERE id=?",(request.current_user,)).fetchone()
    if not row:
        # 匿名用户返回基础信息
        conn.close()
        return jsonify({"success":True,"user":{"id":request.current_user,"nickname":"暖暖用户","login_type":"anonymous","coins":0,"diary_count":0,"chat_count":0}})
    diary_count=conn.execute("SELECT COUNT(*) FROM diaries WHERE user_id=?",(row["id"],)).fetchone()[0]
    chat_count=conn.execute("SELECT COUNT(*) FROM chat_messages WHERE user_id=? AND role='user'",(row["id"],)).fetchone()[0]
    pts=conn.execute("SELECT balance FROM points WHERE user_id=?",(row["id"],)).fetchone()
    coins=pts["balance"] if pts else 0
    conn.close()
    return jsonify({"success":True,"user":{"id":row["id"],"email":row["email"],"nickname":row["nickname"],"coins":coins,"diary_count":diary_count,"chat_count":chat_count}})

@app.route("/api/v1/auth/me", methods=["PUT"])
@require_jwt
def auth_update():
    data=request.get_json(silent=True) or {}
    conn=get_db()
    updates={}
    if "nickname" in data: updates["nickname"]=data["nickname"]
    if updates:
        for k,v in updates.items():
            conn.execute(f"UPDATE users SET {k}=? WHERE id=?",(v,request.current_user))
        conn.commit()
    row=conn.execute("SELECT * FROM users WHERE id=?",(request.current_user,)).fetchone()
    conn.close()
    return jsonify({"success":True,"user":{"id":row["id"],"email":row["email"],"nickname":row["nickname"]}})

@app.route("/api/v1/auth/login_guest", methods=["POST"])
def auth_guest():
    uid=f"guest_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
    token=make_jwt(uid,"guest")
    return jsonify({"success":True,"token":token,"user":{"id":uid,"nickname":"访客","login_type":"guest"}})

# ===== 对话 =====
# 情绪词典（替代小程序emotionClassifier.js）
EMOTION_DIC = {
    "happy": {"keywords":["开心","高兴","快乐","太棒了","幸福","哈哈","好棒","完美","笑了","满足"],"label":"愉悦"},
    "sad": {"keywords":["难过","伤心","哭","失落","悲伤","沮丧","心累","委屈","失望","低落"],"label":"低落"},
    "anxious": {"keywords":["焦虑","烦","压力","担心","怕","慌","紧张","不安","失眠","崩溃"],"label":"焦虑"},
    "angry": {"keywords":["生气","愤怒","火大","不爽","讨厌","离谱","气死","恶心"],"label":"烦躁"},
    "calm": {"keywords":["平静","还好","没事","行","可以","嗯","好","放松","舒服","安心"],"label":"平静"},
}

def classify_emotion(text):
    """情绪分类"""
    if not text: return {"emotion":"calm","label":"平静","intensity":1}
    scores={}
    for em,info in EMOTION_DIC.items():
        count=sum(1 for kw in info["keywords"] if kw in text)
        if count>0:
            scores[em]=count
    if not scores:
        return {"emotion":"calm","label":"平静","intensity":1}
    best=max(scores,key=scores.get)
    return {"emotion":best,"label":EMOTION_DIC[best]["label"],"intensity":min(scores[best],5)}

# 记忆检索（替代小程序memory.js）
FACT_WEIGHTS = {
    "emotion_state":100,"allergy":95,"health_info":95,"life_event":90,"dream":85,
    "preference":80,"pet":75,"family":70,"birthday":65,"name":60,"work":55,"plan":50,
    "habit":45,"important_date":40,"general_fact":10,"custom":10,"other":5
}
LAYER_WEIGHTS = {"identity":1.0,"pattern":0.8,"emotion":0.7,"style":0.5}

def get_memory_context(user_id, text, top_k=5):
    """检索记忆上下文（分层权重排序）"""
    conn=get_db()
    results=[]
    # 第一阶段：精确匹配fact_type
    keywords_map={"生日":["birthday","important_date"],"名字":["name"],"过敏":["allergy"],
                  "纪念日":["important_date"],"喜欢":["preference"],"宠物":["pet"],"家庭":["family"]}
    for kw,types in keywords_map.items():
        if kw in text:
            for ft in types:
                rows=conn.execute("SELECT * FROM user_facts WHERE user_id=? AND fact_type=? ORDER BY updated_at DESC LIMIT 5",
                                 (user_id,ft)).fetchall()
                for r in rows:
                    weight=FACT_WEIGHTS.get(r["fact_type"],5)*LAYER_WEIGHTS.get(r["fact_layer"],0.5)
                    results.append((weight,r))
    # 第二阶段：兜底查询所有事实，按关键词模糊匹配
    all_rows=conn.execute("SELECT * FROM user_facts WHERE user_id=? ORDER BY updated_at DESC LIMIT 50",
                         (user_id,)).fetchall()
    for r in all_rows:
        fact_text=(r["display_name"] or r["fact_value"] or "").lower()
        # 跳过已精确匹配的
        if any(r["fact_type"]==res[1]["fact_type"] for res in results):
            continue
        for kw in re.split(r"[\s，。！？；：、]", text):
            if len(kw)>=2 and kw in fact_text:
                weight=FACT_WEIGHTS.get(r["fact_type"],5)*LAYER_WEIGHTS.get(r["fact_layer"],0.5)
                results.append((weight,r))
                break
    # 排序去重
    seen=set()
    final=[]
    for weight,r in sorted(results,key=lambda x:-x[0])[:top_k]:
        if r["id"] not in seen:
            seen.add(r["id"])
            label=r["fact_type"]
            val=r["display_name"] or r["fact_value"]
            final.append(f"【用户{label}】{val}")
    conn.close()
    return "\n".join(final)

def get_emotion_memory(user_id, text):
    """检索情绪相关记忆"""
    emotion=classify_emotion(text)
    conn=get_db()
    # 查询温暖瞬间
    warm=conn.execute("SELECT summary,comment FROM warm_moments WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
                     (user_id,)).fetchall()
    warm_text=""
    if warm:
        warm_text="\n温暖瞬间：\n"+("\n".join(f"{i+1}. {w['summary']}（{w['comment']}）" for i,w in enumerate(warm)))
    # 查询情绪/模式层事实
    emotion_facts=conn.execute("SELECT * FROM user_facts WHERE user_id=? AND fact_layer IN ('emotion','pattern') ORDER BY updated_at DESC LIMIT 10",
                              (user_id,)).fetchall()
    ef_text=""
    if emotion_facts:
        ef_text="\n【用户的情绪与模式记忆】\n"+("\n".join(f"{i+1}. {e['display_name'] or e['fact_value']}" for i,e in enumerate(emotion_facts)))
    conn.close()
    return {"emotion":emotion["label"],"warm":warm_text,"emotion_facts":ef_text}

@app.route("/api/v1/chat", methods=["POST"])
@require_jwt
def chat():
    data=request.get_json(silent=True) or {}
    msg=data.get("message","").strip()
    if not msg: return jsonify({"success":False,"error":"缺少 message"}),400
    uid=request.current_user
    
    # 1. 情绪分类
    emotion=classify_emotion(msg)
    
    # 2. 记忆检索
    memory_ctx=get_memory_context(uid, msg)
    emo_mem=get_emotion_memory(uid, msg)
    
    # 3. 构建对话上下文
    time_period=get_time_period()
    season=get_season_text()
    term=get_current_term()
    
    system_prompt = f"""你是暖暖，一个温暖、懂倾听的AI陪伴者。
- 语气温暖自然，不肉麻不煽情
- 根据用户的聊天内容做出有针对性的回应
- 适当延续话题，像朋友一样自然对话
- 如果用户聊了心情，给予理解和陪伴
- 回复长度自然，不要太长
- 不要模板化

当前时间：{format_datetime()}
当前时段：{time_period}
季节：{season}
用户情绪：{emotion["label"]}（强度{emotion["intensity"]}）"""

    if memory_ctx:
        system_prompt += f"\n\n关于用户的记忆：\n{memory_ctx}"
    if emo_mem["warm"]:
        system_prompt += f"\n\n{emo_mem['warm']}"
    
    # 4. 调用AI（先混元→降级底座）
    ai_reply=call_ai_with_system(system_prompt, msg, max_tokens=800, temperature=0.7)
    if not ai_reply:
        ai_reply="我在呢，继续说。"
    
    # 5. 保存聊天记录
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO chat_messages (user_id,role,content,emotion,created_at) VALUES (?,?,?,?,?)",
                (uid,"user",msg,emotion["label"],now))
    conn.execute("INSERT INTO chat_messages (user_id,role,content,created_at) VALUES (?,?,?,?)",
                (uid,"assistant",ai_reply,now))
    conn.commit(); conn.close()
    
    return jsonify({"success":True,"content":ai_reply,"emotion":emotion["label"]})

@app.route("/api/v1/chat/history", methods=["GET"])
@require_jwt
def chat_history():
    conn=get_db()
    rows=conn.execute("SELECT * FROM chat_messages WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
                     (request.current_user,)).fetchall()
    conn.close()
    msgs=[{"role":r["role"],"content":r["content"],"emotion":r["emotion"],"created_at":r["created_at"]} for r in reversed(rows)]
    return jsonify({"success":True,"messages":msgs})

# ===== 事实/记忆管理 =====
@app.route("/api/v1/facts", methods=["GET"])
@require_jwt
def get_facts():
    conn=get_db()
    rows=conn.execute("SELECT * FROM user_facts WHERE user_id=? ORDER BY updated_at DESC LIMIT 50",
                     (request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"facts":[dict(r) for r in rows]})

@app.route("/api/v1/facts", methods=["POST"])
@require_jwt
def set_fact():
    data=request.get_json(silent=True) or {}
    fact_type=data.get("type","other")
    fact_value=data.get("value","")
    fact_layer=data.get("layer","identity")
    display_name=data.get("display_name","") or fact_value
    if not fact_value: return jsonify({"success":False,"error":"缺少 value"}),400
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO user_facts (user_id,fact_type,fact_value,fact_layer,display_name,source,confidence,weight,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (request.current_user,fact_type,fact_value,fact_layer,display_name,"user",1.0,10,now,now))
    conn.commit(); conn.close()
    return jsonify({"success":True,"message":"已保存"})

@app.route("/api/v1/facts/search", methods=["POST"])
@require_jwt
def search_facts():
    """关键词搜索事实（替代小程序getFactsByHttp的关键词评分逻辑）"""
    data=request.get_json(silent=True) or {}
    keyword=data.get("keyword","").strip().lower()
    conn=get_db()
    rows=conn.execute("SELECT * FROM user_facts WHERE user_id=? ORDER BY updated_at DESC LIMIT 50",
                     (request.current_user,)).fetchall()
    conn.close()
    if not keyword:
        return jsonify({"success":True,"facts":[dict(r) for r in rows]})
    # 评分排序
    scored=[]
    for r in rows:
        score=0
        ft=(r["fact_type"] or "").lower()
        fv=(r["fact_value"] or "").lower()
        dn=(r["display_name"] or "").lower()
        if ft==keyword: score+=100
        elif keyword in ft: score+=80
        if keyword in fv: score+=60
        if keyword in dn: score+=40
        if score>0:
            scored.append((score,r))
    scored.sort(key=lambda x:-x[0])
    return jsonify({"success":True,"facts":[dict(r) for _,r in scored[:20]]})

@app.route("/api/v1/facts/<int:fact_id>", methods=["DELETE"])
@require_jwt
def delete_fact(fact_id):
    conn=get_db()
    conn.execute("DELETE FROM user_facts WHERE id=? AND user_id=?",(fact_id,request.current_user))
    conn.commit(); conn.close()
    return jsonify({"success":True})

# ===== 日记 =====
@app.route("/api/v1/diary/generate", methods=["POST"])
@require_jwt
def generate_diary():
    uid=request.current_user
    today_str=date.today().isoformat()
    conn=get_db()
    # 1. 查今日是否已有日记
    existing=conn.execute("SELECT * FROM diaries WHERE user_id=? AND date=?",(uid,today_str)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success":True,"diary_content":existing["content"],"diary_date":today_str,"exists":True})
    # 2. 获取聊天素材（上次日记以来的聊天）
    now_dt=datetime.now().isoformat()
    last_diary=conn.execute("SELECT MAX(date) as last_date FROM diaries WHERE user_id=?",(uid,)).fetchone()
    last_date=last_diary["last_date"] or "2000-01-01"
    chats=conn.execute("SELECT * FROM chat_messages WHERE user_id=? AND role='user' AND created_at>=? ORDER BY created_at ASC LIMIT 200",
                      (uid,last_date)).fetchall()
    conn.close()
    if not chats:
        return jsonify({"success":False,"diary_content":"今天还没有聊天记录，去和暖暖聊聊天吧","empty":True})
    
    # 3. 做天气头部
    weather_header=f"{format_datetime()}\n\n"
    
    # 4. 调日记引擎
    chat_material="\n".join(f"{'用户'if c['role']=='user'else'暖暖'}：{c['content']}" for c in chats[-50:])
    try:
        resp=requests.post(f"{DIARY_ENGINE}/api/v1/diary/generate",json={
            "user_id":uid,"date":today_str,"chat_material":chat_material[:3000]
        },timeout=30)
        if resp.status_code==200:
            r=resp.json()
            if r.get("success") and r.get("diary_content"):
                diary_text=r["diary_content"]
            else:
                diary_text=None
        else:
            diary_text=None
    except:
        diary_text=None
    
    # 5. 引擎失败→降级AI
    if not diary_text:
        prompt=f"根据以下今天的聊天记录，以第一人称写一篇简短温暖的日记（100-200字）。不要以日期开头。\n\n聊天记录：\n{chat_material[:2000]}"
        diary_text=call_ai(prompt, max_tokens=600, temperature=0.7)
    
    if not diary_text:
        diary_text="今天比较安静，没有太多想记录的。不过有暖暖陪着，也不错。"
    
    full_diary=weather_header+diary_text
    
    # 6. 保存到数据库
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO diaries (user_id,date,content,mood,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                (uid,today_str,full_diary,"平静",now,now))
    conn.commit(); conn.close()
    
    return jsonify({"success":True,"diary_content":full_diary,"diary_date":today_str,"is_fallback":diary_text is None})

@app.route("/api/v1/diary/today", methods=["GET"])
@require_jwt
def diary_today():
    today_str=date.today().isoformat()
    conn=get_db()
    row=conn.execute("SELECT * FROM diaries WHERE user_id=? AND date=?",(request.current_user,today_str)).fetchone()
    conn.close()
    if row:
        return jsonify({"success":True,"has_diary":True,"content":row["content"],"mood":row["mood"],"date":row["date"]})
    return jsonify({"success":True,"has_diary":False,"content":"","date":today_str})

@app.route("/api/v1/diary/list", methods=["GET"])
@require_jwt
def diary_list():
    page=int(request.args.get("page",1))
    per_page=int(request.args.get("per_page",20))
    offset=(page-1)*per_page
    conn=get_db()
    rows=conn.execute("SELECT * FROM diaries WHERE user_id=? ORDER BY date DESC LIMIT ? OFFSET ?",
                     (request.current_user,per_page,offset)).fetchall()
    total=conn.execute("SELECT COUNT(*) FROM diaries WHERE user_id=?",(request.current_user,)).fetchone()[0]
    conn.close()
    return jsonify({"success":True,"diaries":[dict(r) for r in rows],"total":total,"page":page})

# ===== 情绪签（替代小程序emotion_sign场景）=====
@app.route("/api/v1/emotion/sign", methods=["POST"])
@require_jwt
def emotion_sign():
    uid=request.current_user
    now_ts=datetime.now()
    one_month_ago=(datetime.now()-timedelta(days=30)).isoformat()
    conn=get_db()
    # 获取聊天记录
    chats=conn.execute("SELECT * FROM chat_messages WHERE user_id=? AND role='user' AND created_at>=? ORDER BY created_at DESC LIMIT 50",
                      (uid,one_month_ago)).fetchall()
    # 获取日记
    one_month_ago_date=(datetime.now()-timedelta(days=30)).isoformat()[:10]
    diaries=conn.execute("SELECT * FROM diaries WHERE user_id=? AND date>=? ORDER BY date DESC LIMIT 15",
                        (uid,one_month_ago_date)).fetchall()
    conn.close()
    # 组装上下文
    parts=[]
    if chats:
        chat_text="\n".join(c["content"] for c in chats[:20] if c["content"])
        parts.append(f"【聊天记录】\n{chat_text}")
    if diaries:
        diary_text="\n---\n".join(d["content"][:500] for d in diaries[:10] if d["content"])
        parts.append(f"【日记】\n{diary_text}")
    user_context="\n\n".join(parts)
    if len(user_context)>3000:
        user_context=user_context[:3000]+"...(略)"
    
    time_period=get_time_period()
    season_text=get_season_text()
    term=get_current_term()
    date_str=format_datetime()
    
    prompt=f"你是一个温暖、细腻、有洞察力的情绪陪伴者。\n\n"
    prompt+=f"请根据以下用户的聊天记录和日记内容，深入了解他/她的近期生活状态，生成一份「每日情绪签」。\n\n"
    if user_context:
        prompt+=f"【用户近期生活数据】\n{user_context}\n\n"
    else:
        prompt+="（无近期数据）\n\n"
    prompt+=f"今天是{date_str}，{season_text}，{term}。\n\n"
    prompt+="""请严格按以下结构输出，每段换行分隔：

【情绪洞察】
分析用户近期的情绪状态（80-150字）

【今日肯定】
一句温暖肯定的鼓励（30-60字）

【今日行动建议】
一个具体、可操作的小建议（50-100字）

【金句收尾】
一句温暖的收尾金句（20-40字）

⚠️ 防幻觉规则：
1. 只能引用数据中明确写出来的内容
2. 如果数据中提到某人但没说明关系细节，不得编造
3. 如果数据为空或不足以判断，生成通用温暖内容，绝不编造生活细节
4. 宁可内容平淡也绝不说没有数据依据的话
其他要求：温暖走心但不煽情，直接输出四段内容不要额外说明"""
    
    ai_text=call_ai(prompt, max_tokens=800, temperature=0.7)
    if not ai_text:
        ai_text="【情绪洞察】\n今天看起来是平静的一天。\n\n【今日肯定】\n你已经在努力了，这本身就值得肯定。\n\n【今日行动建议】\n试着在阳光下发一会儿呆。\n\n【金句收尾】\n愿今日的你，被世界温柔以待。🌙"
    return jsonify({"success":True,"content":ai_text,"date":date_str})

# ===== 心运小馆（替代小程序heart_fortune场景）=====
@app.route("/api/v1/heart/fortune", methods=["POST"])
@require_jwt
def heart_fortune():
    """每日上上签（简化版）"""
    try:
        prompt="你是一个温暖、细腻的签文写作者。今天夏至，请为用户写一张温暖的每日上上签（50-80字）。直接输出正文。"
        ai_text=call_ai(prompt, max_tokens=400, temperature=0.7)
        if not ai_text:
            ai_text="今天也是充满希望的一天，阳光会照进你的心里。"
        return jsonify({"success":True,"content":ai_text,"date":format_datetime()})
    except Exception as _e:
        import traceback as _tb
        _tb.print_exc()
        return jsonify({"success":False,"error":str(_e)}),500

@app.route("/api/v1/heart/advice", methods=["POST"])
@require_jwt
def heart_advice():
    """生活建议"""
    uid=request.current_user
    one_month_ago=(datetime.now()-timedelta(days=30)).isoformat()
    conn=get_db()
    chats=conn.execute("SELECT * FROM chat_messages WHERE user_id=? AND role='user' AND created_at>=? ORDER BY created_at DESC LIMIT 20",
                      (uid,one_month_ago)).fetchall()
    conn.close()
    parts=[]
    if chats:
        chat_text="\n".join(c["content"] for c in chats[:8] if c["content"])
        parts.append(f"【聊天记录】\n{chat_text}")
    user_context="\n\n".join(parts)
    season_text=get_season_text()
    
    prompt=f"你是一个温暖、懂生活的生活建议师。\n\n"
    if user_context:
        prompt+=f"以下是用户近期的生活状态：\n{user_context}\n\n"
    else:
        prompt+="（无近期数据）\n\n"
    prompt+=f"今天是{season_text}。\n\n"
    prompt+="""请为用户写一条暖心的生活建议（60-100字）。要求：
1. 贴合用户近期聊天中透露的生活状态
2. 具体可操作，比如推荐一件今天可以尝试的小事
3. 温暖但不肉麻，像朋友在跟你聊天
4. 不模板化、不出现迷信表述
直接输出建议正文。"""
    
    ai_text=call_ai(prompt, max_tokens=350, temperature=0.7)
    if not ai_text:
        ai_text="今天试着在阳光下发一会儿呆，什么都不想，只是感受。"
    return jsonify({"success":True,"content":ai_text})

@app.route("/api/v1/heart/healing", methods=["POST"])
@require_jwt
def heart_healing():
    """情绪疗愈引导"""
    uid=request.current_user
    one_month_ago=(datetime.now()-timedelta(days=30)).isoformat()
    conn=get_db()
    chats=conn.execute("SELECT * FROM chat_messages WHERE user_id=? AND role='user' AND created_at>=? ORDER BY created_at DESC LIMIT 30",
                      (uid,one_month_ago)).fetchall()
    conn.close()
    parts=[]
    if chats:
        chat_text="\n".join(c["content"] for c in chats[:12] if c["content"])
        parts.append(f"【聊天记录】\n{chat_text}")
    user_context="\n\n".join(parts)
    time_period=get_time_period()
    season_text=get_season_text()
    
    prompt=f"你是一个温暖、细腻的疗愈引导师。\n\n"
    if user_context:
        prompt+=f"以下是用户近期的生活状态：\n{user_context}\n\n"
    else:
        prompt+="（无近期数据）\n\n"
    prompt+=f"现在是{time_period}，{season_text}。\n\n"
    prompt+="""请根据用户当前的状态，写一段情绪疗愈引导（150-250字）。要求：
1. 先用一句话理解用户可能的感受
2. 然后引导一段呼吸/放松练习，有具体步骤
3. 如果数据为空，用当下时节做通用引导
4. 用「让我们」「你可以」等温和引导
直接输出引导正文。"""
    
    ai_text=call_ai(prompt, max_tokens=500, temperature=0.7)
    if not ai_text:
        ai_text="找一个舒服的姿势，闭上眼睛，深呼吸三次。感受空气进入身体，带走一天的疲惫。你做得很好。"
    return jsonify({"success":True,"content":ai_text})

# ===== 梦境分析（替代小程序dream_analysis场景）=====
@app.route("/api/v1/dream/analyze", methods=["POST"])
@require_jwt
def dream_analyze():
    data=request.get_json(silent=True) or {}
    dream_content=data.get("dream","").strip() or data.get("message","").strip()
    if not dream_content: return jsonify({"success":False,"error":"请描述你的梦境"}),400
    
    uid=request.current_user
    two_weeks_ago=(datetime.now()-timedelta(days=14)).isoformat()
    conn=get_db()
    chats=conn.execute("SELECT * FROM chat_messages WHERE user_id=? AND role='user' AND created_at>=? ORDER BY created_at DESC LIMIT 25",
                      (uid,two_weeks_ago)).fetchall()
    conn.close()
    parts=[]
    if chats:
        parts.append("聊天内容：\n"+("\n".join(c["content"] for c in chats[:12] if c["content"])))
    user_context="\n\n".join(parts)
    if len(user_context)>2000:
        user_context=user_context[:2000]+"...(略)"
    
    prompt=f"你是一个温暖、有心理学素养的梦境陪伴者。\n\n"
    prompt+=f"【用户描述的梦境】\n{dream_content}\n\n"
    if user_context:
        prompt+=f"【梦境主人的近期生活数据】\n{user_context}\n\n"
    else:
        prompt+="（无近期数据）\n\n"
    prompt+="""请按以下结构输出梦境解读：

【梦境解析】
分析梦境中可能反映的情绪（80-150字）
用「也许」「可能反映了」等温和开放表达

【温暖陪伴】
一句理解和支持的话语（30-60字）

【生活建议】
一个温和、具体的小建议（50-100字）

⚠️ 防幻觉规则：
1. 只能引用数据中明确存在的内容
2. 不得编造任何不存在的人物或事件
3. 如果生活数据为空，只能基于梦境本身做普遍性解析
4. 绝对不允许算命、周公解梦、吉凶预测"""
    
    ai_text=call_ai(prompt, max_tokens=800, temperature=0.7)
    if not ai_text:
        ai_text="梦里的事，也许反映了最近的心事。愿意多说说吗？暖暖在听。"
    return jsonify({"success":True,"content":ai_text,"dream":dream_content})

# ===== 月度回顾 =====
@app.route("/api/v1/review/monthly", methods=["POST"])
@require_jwt
def monthly_review():
    data=request.get_json(silent=True) or {}
    year_month=data.get("month","") or datetime.now().strftime("%Y-%m")
    uid=request.current_user
    
    # 查当月日记
    ym_parts=year_month.split("-")
    start_date=f"{ym_parts[0]}-{ym_parts[1]}-01"
    import calendar
    last_day=calendar.monthrange(int(ym_parts[0]),int(ym_parts[1]))[1]
    end_date=f"{ym_parts[0]}-{ym_parts[1]}-{last_day}"
    
    conn=get_db()
    diaries=conn.execute("SELECT * FROM diaries WHERE user_id=? AND date>=? AND date<=? ORDER BY date ASC",
                        (uid,start_date,end_date)).fetchall()
    conn.close()
    if not diaries:
        return jsonify({"success":True,"content":"这个月还没有写日记，去和暖暖聊聊天，写下第一篇日记吧","month":year_month,"empty":True})
    
    diary_texts="\n---\n".join(f"{d['date']}：{d['content'][:500]}" for d in diaries if d["content"])[:3000]
    
    prompt=f"请根据以下当月日记内容，为用户生成月度回顾（{year_month}）。\n\n"
    prompt+=f"日记内容：\n{diary_texts}\n\n"
    prompt+="""请按以下结构输出：

【本月情绪曲线】
这个月情绪变化的整体描述（60-100字）

【高频关键词】
3-5个主题或关键词

【最值得记住的瞬间】
选2-3个时刻，温暖笔触记录

【暖暖的月度观察】
以「暖暖」口吻写3-4句话观察"""
    
    ai_text=call_ai(prompt, max_tokens=800, temperature=0.7)
    if not ai_text:
        ai_text=f"这个月（{year_month}）你写了几篇日记，记录了不少生活的点滴。继续和暖暖聊聊天吧。"
    
    # 保存
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT OR REPLACE INTO monthly_reviews (user_id,month,content,created_at) VALUES (?,?,?,?)",
                (uid,year_month,ai_text,now))
    conn.commit(); conn.close()
    
    return jsonify({"success":True,"content":ai_text,"month":year_month})

# ===== 暖忆寄语 =====
@app.route("/api/v1/blessing", methods=["POST"])
@require_jwt
def warm_blessing():
    data=request.get_json(silent=True) or {}
    context=data.get("context","")
    prompt=f"你是一个温柔细腻的AI朋友，擅长根据用户的聊天内容写一句温暖的寄语。\n\n"
    if context:
        prompt+=f"参考信息：\n{context}\n\n"
    prompt+="""要求：
1. 温暖治愈，像朋友在耳边轻声说话
2. 如果有参考信息，结合其中内容
3. 如果没有，写一段通用的温暖寄语
4. 长度60-120字
5. 结尾加上「—— 暖暖 🌙」"""
    
    ai_text=call_ai(prompt, max_tokens=300, temperature=0.8)
    if not ai_text:
        ai_text="愿你今夜安睡，明日醒来，阳光正好，花香满径。🌙"
    return jsonify({"success":True,"content":ai_text})

# ===== 意图识别 =====
INTENT_KEYWORDS = {
    "diary": ["写日记","生成日记","记日记","今天的日记","帮我写日记","写一篇日记"],
    "reminder": ["提醒我","记得","别忘了","帮我记","设置提醒","提醒"],
    "review": ["月度回顾","月度总结","这个月怎么样","月报","本月总结","月度报告"],
    "saveClipboard": ["剪贴板","复制到日记","保存到日记","剪贴板内容"],
}
INTENT_ACTION_MAP = {
    "openAnnotation": ["批注","标注","图片批注","标记照片"],
    "generateDiary": ["生成日记","写日记","写一篇日记"],
    "saveClipboard": ["剪贴板","复制的内容","保存剪贴板"],
}

@app.route("/api/v1/intent/match", methods=["POST"])
@require_jwt
def match_intent():
    data=request.get_json(silent=True) or {}
    text=data.get("text","").strip()
    if not text: return jsonify({"success":False,"error":"缺少 text"}),400
    
    # 先遍历动作映射
    for action,keywords in INTENT_ACTION_MAP.items():
        for kw in keywords:
            if kw in text:
                return jsonify({"success":True,"intent":action,"matched":kw})
    # 再遍历场景
    for scene,keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return jsonify({"success":True,"intent":scene,"matched":kw})
    return jsonify({"success":True,"intent":"chat","matched":None})

# ===== 提醒 =====
REMINDER_PATTERNS = [
    (r"(生日|纪念日)[：: ]*(\S+).*?(\d{1,2})月(\d{1,2})日", "anniversary"),
    (r"(下周[一二三四五六日日]|[明后]天|周[一二三四五六日日])\s*(.*?)(?:[，,。.]|$)", "relative"),
    (r"(每年|每月的?)?(\d{1,2})月(\d{1,2})日\s*(.*?)(?:[，,。.]|$)", "date"),
    (r"(每天|每周|每月)\s*(.*?)(?:[，,。.]|$)", "repeat"),
]

@app.route("/api/v1/reminder/parse", methods=["POST"])
@require_jwt
def parse_reminder():
    data=request.get_json(silent=True) or {}
    text=data.get("text","").strip()
    if not text: return jsonify({"success":False,"error":"缺少 text"}),400
    for pat,ptype in REMINDER_PATTERNS:
        m=re.search(pat,text)
        if m:
            return jsonify({"success":True,"has_reminder":True,"matched":m.group(0),"type":ptype,"text":text})
    return jsonify({"success":True,"has_reminder":False,"text":text})

@app.route("/api/v1/reminder/create", methods=["POST"])
@require_jwt
def create_reminder():
    data=request.get_json(silent=True) or {}
    name=data.get("name",""); rtype=data.get("type","general")
    due_date=data.get("date",""); due_time=data.get("time","")
    if not name or not due_date: return jsonify({"success":False,"error":"缺少 name 或 date"}),400
    now=datetime.now().isoformat()
    conn=get_db()
    # 查重
    existing=conn.execute("SELECT id FROM reminders WHERE user_id=? AND name=? AND due_date=?",(request.current_user,name,due_date)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success":False,"error":"提醒已存在"}),409
    conn.execute("INSERT INTO reminders (user_id,name,type,due_date,due_time,priority,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (request.current_user,name,rtype,due_date,due_time,"normal","pending",now,now))
    conn.commit(); conn.close()
    return jsonify({"success":True,"message":f"✅ 已创建提醒：{name}"})

@app.route("/api/v1/reminder/list", methods=["GET"])
@require_jwt
def reminder_list():
    conn=get_db()
    rows=conn.execute("SELECT * FROM reminders WHERE user_id=? AND status='pending' ORDER BY due_date ASC, due_time ASC",
                     (request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"reminders":[dict(r) for r in rows]})

@app.route("/api/v1/reminder/<int:rid>", methods=["DELETE"])
@require_jwt
def delete_reminder(rid):
    conn=get_db()
    conn.execute("DELETE FROM reminders WHERE id=? AND user_id=?",(rid,request.current_user))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route("/api/v1/reminder/<int:rid>/done", methods=["POST"])
@require_jwt
def done_reminder(rid):
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("UPDATE reminders SET status='done',updated_at=? WHERE id=? AND user_id=?",(now,rid,request.current_user))
    conn.commit(); conn.close()
    return jsonify({"success":True})

# ===== 纪念日 =====
@app.route("/api/v1/anniversary", methods=["GET"])
@require_jwt
def anniversary_list():
    conn=get_db()
    rows=conn.execute("SELECT * FROM anniversaries WHERE user_id=? ORDER BY date",(request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"anniversaries":[dict(r) for r in rows]})

@app.route("/api/v1/anniversary", methods=["POST"])
@require_jwt
def anniversary_create():
    data=request.get_json(silent=True) or {}
    name=data.get("name","").strip(); adate=data.get("date","").strip()
    atype=data.get("type","birthday")
    if not name or not adate: return jsonify({"success":False,"error":"缺少 name 或 date"}),400
    aid=str(uuid.uuid4())[:8]; now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO anniversaries (id,user_id,name,date,type,created_at) VALUES (?,?,?,?,?,?)",
                (aid,request.current_user,name,adate,atype,now))
    conn.commit(); conn.close()
    return jsonify({"success":True,"anniversary":{"id":aid,"name":name,"date":adate,"type":atype}})

@app.route("/api/v1/anniversary/<anniv_id>", methods=["DELETE"])
@require_jwt
def anniversary_delete(anniv_id):
    conn=get_db()
    conn.execute("DELETE FROM anniversaries WHERE id=? AND user_id=?",(anniv_id,request.current_user))
    conn.commit(); conn.close()
    return jsonify({"success":True})

# ===== 人生事件/生活档案 =====
@app.route("/api/v1/life/timeline", methods=["GET"])
@require_jwt
def life_timeline():
    conn=get_db()
    rows=conn.execute("SELECT * FROM life_events WHERE user_id=? ORDER BY year DESC",(request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"events":[dict(r) for r in rows]})

@app.route("/api/v1/life/event", methods=["POST"])
@require_jwt
def life_event_create():
    data=request.get_json(silent=True) or {}
    year=data.get("year","").strip(); title=data.get("title","").strip()
    desc=data.get("description",""); etype=data.get("event_type","milestone")
    if not year or not title: return jsonify({"success":False,"error":"缺少 year 或 title"}),400
    eid=str(uuid.uuid4())[:8]; now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO life_events (id,user_id,year,title,description,event_type,created_at) VALUES (?,?,?,?,?,?,?)",
                (eid,request.current_user,year,title,desc,etype,now))
    conn.commit(); conn.close()
    return jsonify({"success":True,"event":{"id":eid,"year":year,"title":title,"description":desc,"type":etype}})

@app.route("/api/v1/life/event/<event_id>", methods=["DELETE"])
@require_jwt
def life_event_delete(event_id):
    conn=get_db()
    conn.execute("DELETE FROM life_events WHERE id=? AND user_id=?",(event_id,request.current_user))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route("/api/v1/life/archive", methods=["GET"])
@require_jwt
def life_archive():
    try:
        resp=requests.post(f"{BASE_ENGINE}/chat",json={
            "user_id":request.current_user,
            "message":"根据你对我所有的了解，帮我总结一份我的人生档案：我的出身、成长、重要经历、性格特点。"
        },timeout=20)
        return jsonify({"success":True,"content":resp.json().get("content","")})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),502

# ===== 情绪总览 =====
@app.route("/api/v1/emotion/overview", methods=["GET"])
@require_jwt
def emotion_overview():
    days=int(request.args.get("days",30))
    start_date=(datetime.now()-timedelta(days=days)).isoformat()
    conn=get_db()
    rows=conn.execute("SELECT emotion,COUNT(*) as cnt FROM chat_messages WHERE user_id=? AND emotion!='' AND created_at>=? GROUP BY emotion ORDER BY cnt DESC",
                     (request.current_user,start_date)).fetchall()
    conn.close()
    emotions=[{"emotion":r["emotion"],"count":r["cnt"]} for r in rows]
    return jsonify({"success":True,"emotions":emotions,"days":days,"total":sum(e["count"] for e in emotions)})

@app.route("/api/v1/emotion/timeline", methods=["GET"])
@require_jwt
def emotion_timeline():
    days=int(request.args.get("days",7))
    start_date=(datetime.now()-timedelta(days=days)).isoformat()
    conn=get_db()
    rows=conn.execute("SELECT DATE(created_at) as d,emotion,COUNT(*) as cnt FROM chat_messages WHERE user_id=? AND emotion!='' AND created_at>=? GROUP BY d,emotion ORDER BY d",
                     (request.current_user,start_date)).fetchall()
    conn.close()
    timeline={}
    for r in rows:
        d=r["d"]
        if d not in timeline: timeline[d]={}
        timeline[d][r["emotion"]]=r["cnt"]
    return jsonify({"success":True,"timeline":timeline,"days":days})

# ===== 回响谷（复用V3逻辑）=====
def _sq_post_to_dict(row):
    return {"id":row[0],"user_id":row[1],"content":row[2],"emotion_tag":row[3],"topic":row[4],
            "images":row[5],"likes":row[6],"comments_count":row[7],"created_at":row[8],"updated_at":row[9]}

@app.route("/api/v1/square/posts", methods=["GET"])
@require_jwt
def square_posts():
    topic=request.args.get("topic","")
    page=int(request.args.get("page",1))
    per_page=min(int(request.args.get("per_page",20)),50)
    offset=(page-1)*per_page
    conn=get_db()
    if topic:
        rows=conn.execute("SELECT * FROM square_posts WHERE topic=? ORDER BY created_at DESC LIMIT ? OFFSET ?",(topic,per_page,offset)).fetchall()
        total=conn.execute("SELECT COUNT(*) FROM square_posts WHERE topic=?",(topic,)).fetchone()[0]
    else:
        rows=conn.execute("SELECT * FROM square_posts ORDER BY created_at DESC LIMIT ? OFFSET ?",(per_page,offset)).fetchall()
        total=conn.execute("SELECT COUNT(*) FROM square_posts").fetchone()[0]
    conn.close()
    return jsonify({"success":True,"posts":[dict(r) for r in rows],"total":total,"page":page})

@app.route("/api/v1/square/posts", methods=["POST"])
@require_jwt
def square_create():
    data=request.get_json(silent=True) or {}
    content=data.get("content","").strip()
    if not content: return jsonify({"success":False,"error":"缺少 content"}),400
    emotion_tag=data.get("emotion_tag","")
    topic=data.get("topic","")
    post_id=str(uuid.uuid4())[:8]
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO square_posts (id,user_id,content,emotion_tag,topic,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
                (post_id,request.current_user,content,emotion_tag,topic,now,now))
    if topic:
        conn.execute("UPDATE square_topics SET post_count=post_count+1 WHERE name=?",(topic,))
    conn.commit(); conn.close()
    return jsonify({"success":True,"post":{"id":post_id,"content":content,"emotion_tag":emotion_tag,"topic":topic,"likes":0,"comments_count":0,"created_at":now}})

@app.route("/api/v1/square/posts/<post_id>", methods=["GET"])
@require_jwt
def square_post_detail(post_id):
    conn=get_db()
    row=conn.execute("SELECT * FROM square_posts WHERE id=?",(post_id,)).fetchone()
    if not row: conn.close(); return jsonify({"success":False,"error":"帖子不存在"}),404
    comments=conn.execute("SELECT * FROM square_comments WHERE post_id=? ORDER BY created_at",(post_id,)).fetchall()
    conn.close()
    post=dict(row)
    post["comments"]=[{"id":c["id"],"user_id":c["user_id"],"content":c["content"],"created_at":c["created_at"]} for c in comments]
    return jsonify({"success":True,"post":post})

@app.route("/api/v1/square/posts/<post_id>/like", methods=["POST"])
@require_jwt
def square_toggle_like(post_id):
    conn=get_db()
    existing=conn.execute("SELECT * FROM square_likes WHERE post_id=? AND user_id=?",(post_id,request.current_user)).fetchone()
    if existing:
        conn.execute("DELETE FROM square_likes WHERE post_id=? AND user_id=?",(post_id,request.current_user))
        conn.execute("UPDATE square_posts SET likes=likes-1 WHERE id=?",(post_id,))
        liked=False
    else:
        conn.execute("INSERT INTO square_likes (post_id,user_id) VALUES (?,?)",(post_id,request.current_user))
        conn.execute("UPDATE square_posts SET likes=likes+1 WHERE id=?",(post_id,))
        liked=True
    likes=conn.execute("SELECT likes FROM square_posts WHERE id=?",(post_id,)).fetchone()[0]
    conn.commit(); conn.close()
    return jsonify({"success":True,"liked":liked,"likes":likes})

@app.route("/api/v1/square/posts/<post_id>/comments", methods=["POST"])
@require_jwt
def square_comment(post_id):
    data=request.get_json(silent=True) or {}
    content=data.get("content","").strip()
    if not content: return jsonify({"success":False,"error":"缺少 content"}),400
    cid=str(uuid.uuid4())[:12]; now=datetime.now().isoformat()
    conn=get_db()
    row=conn.execute("SELECT id FROM square_posts WHERE id=?",(post_id,)).fetchone()
    if not row: conn.close(); return jsonify({"success":False,"error":"帖子不存在"}),404
    conn.execute("INSERT INTO square_comments (id,post_id,user_id,content,created_at) VALUES (?,?,?,?,?)",(cid,post_id,request.current_user,content,now))
    conn.execute("UPDATE square_posts SET comments_count=comments_count+1 WHERE id=?",(post_id,))
    conn.commit(); conn.close()
    return jsonify({"success":True,"comment":{"id":cid,"user_id":request.current_user,"content":content,"created_at":now}})

@app.route("/api/v1/square/topics", methods=["GET"])
@require_jwt
def square_topics():
    conn=get_db()
    rows=conn.execute("SELECT * FROM square_topics ORDER BY post_count DESC LIMIT 30").fetchall()
    conn.close()
    return jsonify({"success":True,"topics":[dict(r) for r in rows]})

@app.route("/api/v1/square/topics", methods=["POST"])
@require_jwt
def square_create_topic():
    data=request.get_json(silent=True) or {}
    name=data.get("name","").strip()
    if not name: return jsonify({"success":False,"error":"缺少 name"}),400
    tid=str(uuid.uuid4())[:8]; now=datetime.now().isoformat()
    conn=get_db()
    try:
        conn.execute("INSERT INTO square_topics (id,name,description,created_at) VALUES (?,?,?,?)",(tid,name,data.get("description",""),now))
        conn.commit(); conn.close()
        return jsonify({"success":True,"topic":{"id":tid,"name":name,"post_count":0}})
    except:
        conn.close()
        return jsonify({"success":False,"error":"话题已存在"}),409

@app.route("/api/v1/square/feed", methods=["GET"])
@require_jwt
def square_feed():
    page=int(request.args.get("page",1))
    per_page=min(int(request.args.get("per_page",20)),50)
    offset=(page-1)*per_page
    conn=get_db()
    rows=conn.execute("SELECT *, (likes*2 + comments_count*3) as heat FROM square_posts ORDER BY heat DESC, created_at DESC LIMIT ? OFFSET ?",(per_page,offset)).fetchall()
    total=conn.execute("SELECT COUNT(*) FROM square_posts").fetchone()[0]
    conn.close()
    return jsonify({"success":True,"posts":[dict(r) for r in rows],"total":total,"page":page})

# ===== 家庭 =====
@app.route("/api/v1/family", methods=["POST"])
@require_jwt
def family_create():
    data=request.get_json(silent=True) or {}
    name=data.get("name","").strip()
    if not name: return jsonify({"success":False,"error":"缺少 name"}),400
    fid=str(uuid.uuid4())[:8]; now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO families (id,name,owner,created_at) VALUES (?,?,?,?)",(fid,name,request.current_user,now))
    conn.execute("INSERT INTO family_members (family_id,user_id,role,joined_at) VALUES (?,?,?,?)",(fid,request.current_user,"owner",now))
    conn.commit(); conn.close()
    return jsonify({"success":True,"family":{"id":fid,"name":name,"owner":request.current_user}})

@app.route("/api/v1/family", methods=["GET"])
@require_jwt
def family_list():
    conn=get_db()
    rows=conn.execute("SELECT f.*,fm.role FROM families f JOIN family_members fm ON f.id=fm.family_id WHERE fm.user_id=? ORDER BY f.created_at DESC",
                     (request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"families":[dict(r) for r in rows]})

@app.route("/api/v1/family/chat", methods=["POST"])
@require_jwt
def family_chat():
    data=request.get_json(silent=True) or {}
    msg=data.get("message","").strip()
    if not msg: return jsonify({"success":False,"error":"缺少 message"}),400
    try:
        resp=requests.post(f"{BASE_ENGINE}/chat",json={"user_id":f"family_{request.current_user}","message":msg},timeout=15)
        return jsonify({"success":True,"content":resp.json().get("content","")})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}),502

# ===== 用户相关 =====
@app.route("/api/v1/user/profile", methods=["GET"])
@require_jwt
def user_profile():
    conn=get_db()
    diary_count=conn.execute("SELECT COUNT(*) FROM diaries WHERE user_id=?",(request.current_user,)).fetchone()[0]
    chat_count=conn.execute("SELECT COUNT(*) FROM chat_messages WHERE user_id=? AND role='user'",(request.current_user,)).fetchone()[0]
    pts=conn.execute("SELECT balance FROM points WHERE user_id=?",(request.current_user,)).fetchone()
    coins=pts["balance"] if pts else 0
    conn.close()
    return jsonify({"success":True,"user":{"id":request.current_user,"login_type":request.login_type,"diary_count":diary_count,"chat_count":chat_count,"coins":coins}})

@app.route("/api/v1/user/clear", methods=["POST"])
@require_jwt
def clear_user():
    try: requests.post(f"{BASE_ENGINE}/clear",json={"user_id":request.current_user},timeout=5)
    except: pass
    return jsonify({"success":True})

# ===== 那年今日 =====
@app.route("/api/v1/memory/thisday", methods=["GET"])
@require_jwt
def this_day():
    today_md=date.today().strftime("%m-%d")
    conn=get_db()
    rows=conn.execute("SELECT * FROM diaries WHERE user_id=? AND strftime('%m-%d',date)=? ORDER BY date DESC LIMIT 3",
                     (request.current_user,f"{today_md[:2]}-{today_md[3:]}")).fetchall()
    conn.close()
    if rows:
        return jsonify({"success":True,"has_memory":True,"entries":[{"date":r["date"],"content":r["content"][:200]} for r in rows],"month_day":today_md})
    return jsonify({"success":True,"has_memory":False,"month_day":today_md})

# ===== Pi生态 =====
@app.route("/api/v1/pi/auth/challenge", methods=["GET"])
def pi_challenge():
    return jsonify({"success":True,"challenge":hashlib.sha256(f"{time.time()}_nuan".encode()).hexdigest()[:16],"expires_in":300})

@app.route("/api/v1/pi/auth/login", methods=["POST"])
def pi_login():
    data=request.get_json(silent=True) or {}
    uid=f"pi_{hashlib.md5(data.get('auth','').encode()).hexdigest()[:12]}"
    return jsonify({"success":True,"token":make_jwt(uid,"pinetwork"),"user":{"id":uid,"login_type":"pinetwork","is_new":True}})

@app.route("/api/v1/pi/pay/create", methods=["POST"])
@require_jwt
def pi_pay_create():
    data=request.get_json(silent=True) or {}
    plans={"basic":{"pi_amount":1,"name":"基础订阅"},"premium":{"pi_amount":3,"name":"高级订阅"}}
    p=plans.get(data.get("plan_id","basic"),plans["basic"])
    return jsonify({"success":True,"order_id":f"pi_order_{int(time.time())}","pi_amount":p["pi_amount"],"plan_name":p["plan_name"],"status":"pending"})

@app.route("/api/v1/pi/pay/callback", methods=["POST"])
def pi_pay_callback():
    print(f"[Pi回调] {json.dumps(request.get_json(silent=True) or {}, ensure_ascii=False)}")
    return jsonify({"success":True})

# ===== 积分/暖币 =====
@app.route("/api/v1/points", methods=["GET"])
@require_jwt
def get_points():
    conn=get_db()
    row=conn.execute("SELECT balance FROM points WHERE user_id=?",(request.current_user,)).fetchone()
    balance=row["balance"] if row else 0
    logs=conn.execute("SELECT * FROM point_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 20",(request.current_user,)).fetchall()
    conn.close()
    return jsonify({"success":True,"balance":balance,"logs":[dict(l) for l in logs]})

@app.route("/api/v1/points/add", methods=["POST"])
@require_jwt
def add_points():
    data=request.get_json(silent=True) or {}
    amount=int(data.get("amount",0))
    reason=data.get("reason","日常签到")
    if amount<=0: return jsonify({"success":False,"error":"无效数量"}),400
    now=datetime.now().isoformat()
    conn=get_db()
    conn.execute("INSERT INTO points (user_id,balance,updated_at) VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET balance=balance+?,updated_at=?",
                (request.current_user,amount,now,amount,now))
    conn.execute("INSERT INTO point_logs (user_id,amount,reason,created_at) VALUES (?,?,?,?)",(request.current_user,amount,reason,now))
    conn.commit()
    balance=conn.execute("SELECT balance FROM points WHERE user_id=?",(request.current_user,)).fetchone()[0]
    conn.close()
    return jsonify({"success":True,"balance":balance,"added":amount,"reason":reason})

# ===== 启动 =====
if __name__=="__main__":
    # 初始化数据库
    init_db()
    from db import ensure_default_user
    ensure_default_user()
    
    print(f"暖忆录·永恒版 API v4.0")
    print(f"端口: {API_PORT}")
    try:
        b_resp = requests.get(f'{BASE_ENGINE}/health',timeout=3)
        print(f"底座: {'✅' if b_resp.status_code==200 else '❌'}")
    except:
        print(f"底座: ❌")
    try:
        d_resp = requests.get(f'{DIARY_ENGINE}/',timeout=3)
        print(f"日记: {'✅' if d_resp.status_code==200 else '❌'}")
    except:
        print(f"日记: ❌")
    try:
        q_resp = requests.get(f'{QDRANT_URL}/',timeout=3)
        print(f"Qdrant: {'✅' if q_resp.status_code==200 else '❌'}")
    except:
        print(f"Qdrant: ❌")
    print(f"全部板块:")
    print(f"  /auth         用户登录/注册")
    print(f"  /chat         个人对话(情感感知+记忆增强)")
    print(f"  /facts        事实记忆管理")
    print(f"  /diary        日记生成/列表")
    print(f"  /emotion      情绪识别/总览")
    print(f"  /emotion/sign 情绪签")
    print(f"  /heart        心运小馆(签文/建议/疗愈)")
    print(f"  /dream        梦境分析")
    print(f"  /review       月度回顾")
    print(f"  /reminder     提醒服务")
    print(f"  /anniversary  纪念日管理")
    print(f"  /square       回响谷广场")
    print(f"  /family       家和空间")
    print(f"  /life         生活档案")
    print(f"  /pi           Pi生态")
    print(f"  /user         用户中心")
    print(f"  /points       积分系统")
    print(f"  /blessing     暖忆寄语")
    print(f"公网: http://61.150.123.162:{API_PORT}")
    from waitress import serve
    serve(app, host="0.0.0.0", port=API_PORT, threads=8)
