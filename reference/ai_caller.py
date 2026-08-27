"""
暖忆录·永恒版 — AI调用工具
封装混元/通义千问API调用，支持重试和降级
"""
import requests, json, time, os
from datetime import datetime

# 混元API配置（从小程序完整版直接沿用）
HUNYUAN_API_URL = "https://api.hunyuan.cloud.tencent.com/v1/chat/completions"
HUNYUAN_API_KEY = os.environ.get("HUNYUAN_API_KEY", "sk-RW0...YfMR")

# 阿里云DashScope（通义千问，小程序降级用）
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", HUNYUAN_API_KEY)

# 底座引擎
BASE_ENGINE = "http://61.150.123.162:6335"

def call_hunyuan(prompt, max_tokens=800, temperature=0.7, timeout=30, system_prompt=None):
    """调用腾讯混元Lite"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        resp = requests.post(HUNYUAN_API_URL, json={
            "model": "hunyuan-lite",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }, headers={
            "Authorization": f"Bearer {HUNYUAN_API_KEY}",
            "Content-Type": "application/json"
        }, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return None
    except Exception as e:
        print(f"[混元] 调用失败: {e}")
        return None

def call_dashscope(prompt, max_tokens=800, temperature=0.7, timeout=15, system_prompt=None):
    """降级：调用阿里云DashScope（通义千问）"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        resp = requests.post(DASHSCOPE_API_URL, json={
            "model": "qwen-max",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }, headers={
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return None
    except Exception as e:
        print(f"[DashScope] 调用失败: {e}")
        return None

def call_ai(prompt, max_tokens=800, temperature=0.7, timeout=30, system_prompt=None, retry=2):
    """主AI调用：先混元→降级通义千问→最后用底座"""
    # 第一次：混元
    for i in range(retry):
        result = call_hunyuan(prompt, max_tokens, temperature, timeout, system_prompt)
        if result:
            return result
        print(f"[AI] 混元第{i+1}次失败，重试...")
    
    # 降级：通义千问
    print("[AI] 混元全部失败，降级通义千问")
    result = call_dashscope(prompt, max_tokens, temperature, 15, system_prompt)
    if result:
        return result
    
    # 最后兜底：底座
    print("[AI] 通义千问也失败，兜底座")
    try:
        resp = requests.post(f"{BASE_ENGINE}/chat", json={
            "user_id": "fallback",
            "message": prompt[:500]
        }, timeout=15)
        content = resp.json().get("content", "")
        if content:
            return content
    except:
        pass
    
    return None

def call_ai_with_system(system_prompt, user_prompt, max_tokens=800, temperature=0.7):
    """带system prompt的AI调用"""
    return call_ai(user_prompt, max_tokens, temperature, 30, system_prompt)

# ===== 时间工具（替代小程序helpers.js）=====
def get_time_period():
    h = datetime.now().hour
    if 5 <= h < 8: return "清晨"
    if 8 <= h < 12: return "上午"
    if 12 <= h < 14: return "中午"
    if 14 <= h < 18: return "下午"
    if 18 <= h < 21: return "傍晚"
    return "晚上"

def get_season():
    m = datetime.now().month
    if 3 <= m <= 5: return "spring"
    if 6 <= m <= 8: return "summer"
    if 9 <= m <= 11: return "autumn"
    return "winter"

def get_season_text(season=None):
    s = season or get_season()
    return {"spring":"春天","summer":"夏天","autumn":"秋天","winter":"冬天"}.get(s, "秋天")

def get_current_term():
    """简单节气判定"""
    m, d = datetime.now().month, datetime.now().day
    terms = [
        (1,5,"小寒"),(1,20,"大寒"),(2,3,"立春"),(2,18,"雨水"),
        (3,5,"惊蛰"),(3,20,"春分"),(4,4,"清明"),(4,19,"谷雨"),
        (5,5,"立夏"),(5,20,"小满"),(6,5,"芒种"),(6,21,"夏至"),
        (7,6,"小暑"),(7,22,"大暑"),(8,7,"立秋"),(8,22,"处暑"),
        (9,7,"白露"),(9,22,"秋分"),(10,8,"寒露"),(10,23,"霜降"),
        (11,7,"立冬"),(11,22,"小雪"),(12,6,"大雪"),(12,21,"冬至")
    ]
    for tm, td, name in terms:
        if m == tm and d >= td:
            return name
    return ""

def format_datetime(dt=None):
    """格式化时间→'2026年6月27日 星期六 10:30'"""
    if not dt:
        dt = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    return f"{dt.year}年{dt.month}月{dt.day}日 {weekdays[dt.weekday()]} {dt.hour:02d}:{dt.minute:02d}"
