#!/usr/bin/env python3
import os
import sys
import json
import requests
import random
from datetime import datetime, timedelta

# 文案库
WORKDAY_MESSAGES = [
    "又是充实的一天，辛苦了！愿你傍晚时光轻松惬意！",
    "工作完成得很好，现在该好好休息了！",
    "今天的努力都值得，来杯咖啡放松一下吧！",
    "下班路上注意安全，记得吃晚饭！",
    "晚上记得留点时间给自己，做自己喜欢的事！",
    "今晚想听什么歌？让音乐治愈你！",
    "早睡早起，明天又是元气满满的一天！",
    "多喝热水，照顾好自己！",
    "愿你今晚做个好梦！",
    "辛苦了，给自己一个拥抱吧！",
    "今晚想玩什么游戏？放松一下！",
    "看一部好电影，享受休闲时光！",
    "散步或运动一下，释放压力！",
    "今晚吃顿好的，犒劳自己！",
    "生活不止工作，还有诗和远方！",
    "读一本好书，陶冶情操！",
    "发挥创意，做点手工或画画！",
    "和朋友聊聊天，分享生活点滴！",
    "冥想或瑜伽，平静内心！",
    "亲近自然，呼吸新鲜空气！",
    "听听播客，学习新知识！",
    "吃点甜食，提升幸福感！",
    "晚安，好梦！",
    "感谢今天的努力，明天继续加油！",
    "你今天做得很好，值得表扬！",
    "保持微笑，明天会更好！",
    "下班啦！自由时间开始！",
    "享受阳光，温暖心灵！",
    "写写日记，记录美好瞬间！"
]

WEEKEND_MESSAGES = [
    "周末快乐！好好休息，享受美好时光！",
    "阳光明媚，适合出门走走！",
    "窝在沙发上看部好电影吧！",
    "美食治愈一切，吃顿好的！",
    "读一本好书，充实心灵！",
    "放松一下，玩玩游戏！",
    "运动一下，保持活力！",
    "和家人朋友聚聚，分享快乐！",
    "亲近自然，呼吸新鲜空气！",
    "睡个好觉，充分休息！"
]

def get_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = {"app_id": app_id, "app_secret": app_secret}
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if data.get("code") != 0:
        print(f"❌ 获取 Token 失败: {data.get('msg')}")
        sys.exit(1)
    
    return data.get("tenant_access_token")

def get_chats(token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"page_size": 50, "user_id_type": "open_id"}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if data.get("code") != 0:
        print(f"❌ 获取群聊列表失败: {data.get('msg')}")
        sys.exit(1)
    
    return data.get("data", {}).get("items", [])

def create_card(message, is_weekend):
    """创建飞书卡片"""
    
    # 根据工作日/周末选择不同的主题色和图标
    if is_weekend:
        title = "🎉 周末祝福"
        color = "green"
        icon = "🌞"
    else:
        title = "🌅 下班祝福"
        color = "blue"
        icon = "💼"
    
    # 获取当前北京时间
    now = datetime.now()
    beijing_time = (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "content": f"{icon} {title}",
                "tag": "plain_text"
            },
            "template": color
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": message,
                    "tag": "lark_md"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "content": f"⏰ {beijing_time}",
                    "tag": "plain_text"
                },
                "extra": {
                    "style": {
                        "align": "right",
                        "color": "grey"
                    }
                }
            }
        ]
    }
    
    return card

def send_message(token, chat_id, message, is_weekend):
    """发送消息（卡片格式）"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "chat_id"}
    
    # 创建卡片
    card = create_card(message, is_weekend)
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
    
    response = requests.post(url, headers=headers, params=params, json=payload)
    data = response.json()
    
    return data.get("code") == 0

def is_weekend():
    """判断是否是周末（北京时间）"""
    now = datetime.now()
    weekday = now.weekday()  # 0=周一, 6=周日
    
    # 北京时间: (weekday + 1) % 7
    beijing_weekday = (weekday + 1) % 7
    
    # 0=周日, 6=周六 是周末
    return beijing_weekday == 0 or beijing_weekday == 6

def main():
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("❌ 缺少 FEISHU_APP_ID 或 FEISHU_APP_SECRET 环境变量")
        sys.exit(1)
    
    print("🔑 获取飞书 Token...")
    token = get_token(app_id, app_secret)
    print("✅ Token 获取成功")
    
    print("📋 获取群聊列表...")
    chats = get_chats(token)
    print(f"✅ 找到 {len(chats)} 个群聊")
    
    if len(chats) == 0:
        print("❌ 没有找到任何群聊")
        sys.exit(1)
    
    # 判断工作日还是周末
    is_weekend_day = is_weekend()
    if is_weekend_day:
        print("📅 今天是周末")
        messages = WEEKEND_MESSAGES
    else:
        print("📅 今天是工作日")
        messages = WORKDAY_MESSAGES
    
    # 随机选择一条消息
    message = random.choice(messages)
    print(f"📝 选中的消息: {message}")
    
    print("📤 开始发送消息...")
    
    success_count = 0
    fail_count = 0
    
    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_name = chat.get("name", "未命名")
        
        print(f"  发送到「{chat_name}」...")
        
        if send_message(token, chat_id, message, is_weekend_day):
            print(f"  ✅ 发送成功")
            success_count += 1
        else:
            print(f"  ❌ 发送失败")
            fail_count += 1
    
    print("=" * 32)
    print(f"✅ 成功: {success_count} 个群聊")
    print(f"❌ 失败: {fail_count} 个群聊")
    print("=" * 32)

if __name__ == "__main__":
    main()
