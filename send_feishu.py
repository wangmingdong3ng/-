#!/usr/bin/env python3
import os
import sys
import json
import requests
import random
from datetime import datetime, timedelta

# 工作日文案（100条）- 轻松有趣
WORKDAY_MESSAGES = [
    # 下班开心类
    "终于下班啦！解放啦！",
    "下班咯！自由时间到！",
    "下班！下班！下班！",
    "今天的任务，已完成！",
    "打卡成功，溜了溜了！",
    "电脑关机，生活开机！",
    "下班快乐，拒绝加班！",
    "今日工作已清零！",
    "下班打卡，走人！",
    "终于可以回家了！",
    
    # 吃货类
    "晚上吃啥？想好了吗？",
    "火锅烧烤走起！",
    "奶茶喝起来！",
    "今晚必须吃顿好的！",
    "点外卖，犒劳自己！",
    "来瓶快乐水！",
    "深夜食堂营业中！",
    "炸鸡啤酒安排上！",
    "饿了吗？开饭啦！",
    "好吃的不能错过！",
    
    # 放松类
    "躺平模式，开启！",
    "沙发就是我的家！",
    "刷剧模式，启动！",
    "手机不离手，快乐跟着走",
    "追剧追到天亮！",
    "葛优躺，舒服！",
    "放松一下，充充电！",
    "刷刷视频，解解压！",
    "游戏时间到！",
    "熬夜冠军，就是我！",
    
    # 睡觉类
    "今晚必须早睡！",
    "睡个好觉，明天见！",
    "失眠是什么？不知道！",
    "熬夜伤身，但我不想睡！",
    "睡觉，睡觉，睡觉！",
    "床在召唤我！",
    "睡饱了，才有精神！",
    "晚安，全世界！",
    "做个美梦！",
    "梦里啥都有！",
    
    # 调皮类
    "今天辛苦，明天继续！",
    "明天又是一样的搬砖！",
    "努力工作，为了躺平！",
    "赚钱就是为了花！",
    "上班为了下班，懂？",
    "摸鱼一时爽，一直摸鱼！",
    "混日子的一天！",
    "这就是生活啊！",
    "活着就是胜利！",
    "今天也是元气满满（假的）",
    
    # 社交类
    "约饭，约饭，约饭！",
    "出来玩啊！",
    "群里吹个牛！",
    "朋友走起，嗨起来！",
    "出来嗨，别宅着！",
    "约个局，放松一下！",
    "八卦时间到！",
    "聊聊今天的事！",
    "吐槽时间开始！",
    "群里的兄弟姐妹们！",
    
    # 自我鼓励类
    "今天也是努力的一天！",
    "加油，打工人！",
    "相信自己，你可以的！",
    "坚持就是胜利！",
    "每天进步一点点！",
    "今天做得不错！",
    "给自己点个赞！",
    "明天会更好！",
    "保持微笑！",
    "生活需要仪式感！",
    
    # 佛系类
    "随缘，随缘，一切随缘！",
    "佛系上班，佛系下班！",
    "无所谓，无所谓！",
    "淡定，淡定！",
    "心态要稳！",
    "别太认真！",
    "开心就好！",
    "一切都会好起来！",
    "差不多就行了！",
    "人生苦短，及时行乐！",
    
    # 实用类
    "记得给手机充电！",
    "记得吃晚饭！",
    "记得给植物浇水！",
    "记得倒垃圾！",
    "记得洗衣服！",
    "记得整理房间！",
    "记得备份文件！",
    "记得关电脑！",
    "记得带伞！",
    "记得爱自己！",
    
    # 周末预告类
    "周末快到了！",
    "再坚持几天！",
    "周末想干嘛？",
    "周末约起来！",
    "周末睡个懒觉！",
    "周末去哪里玩？",
    "周末吃大餐！",
    "周末嗨起来！",
    "周末就是爽！",
    "周末快乐！",
    
    # 随心所欲类
    "想干嘛就干嘛！",
    "爱咋咋地！",
    "管他呢，开心就好！",
    "别想太多！",
    "随心所欲！",
    "放飞自我！",
    "做自己喜欢的事！",
    "人生苦短，开心第一！",
    "快乐最重要！",
    "想干嘛干嘛！"
]

# 周末文案（50条）- 更加放松
WEEKEND_MESSAGES = [
    # 周末快乐类
    "周末快乐！嗨起来！",
    "周末睡到自然醒！",
    "周末就是爽！",
    "周末自由万岁！",
    "周末不工作，真香！",
    "周末随便浪！",
    "周末就是要玩！",
    "周末不加班，开心！",
    "周末模式，开启！",
    "周末心情美美哒！",
    
    # 吃喝类
    "周末大餐安排上！",
    "火锅烧烤走起！",
    "奶茶喝起来！",
    "周末必须吃好！",
    "美食不可辜负！",
    "吃货的周末！",
    "周末吃吃吃！",
    "约饭，约饭！",
    "美食走一波！",
    "周末不减肥！",
    
    # 玩乐类
    "游戏时间到！",
    "刷剧模式，启动！",
    "周末嗨翻天！",
    "出来玩啊！",
    "周末就是玩！",
    "看电影走起！",
    "KTV约起！",
    "游戏开黑！",
    "周末狂欢！",
    "周末尽情嗨！",
    
    # 懒散类
    "周末就是躺平！",
    "宅家模式，开启！",
    "周末葛优躺！",
    "周末睡觉！",
    "周末不洗澡（开玩笑）",
    "周末懒懒懒！",
    "周末混吃等死！",
    "周末刷手机！",
    "周末追剧！",
    "周末啥也不干！",
    
    # 外出类
    "出去走走，透透气！",
    "周末去哪玩？",
    "周末爬山去！",
    "周末逛街去！",
    "周末看电影！",
    "周末聚餐去！",
    "周末户外活动！",
    "周末去旅行！",
    "周末去公园！",
    "周末去海边！",
    
    # 自我奖励类
    "犒劳自己一下！",
    "周末对自己好点！",
    "周末买买买！",
    "周末做SPA！",
    "周末放松一下！",
    "周末享受生活！",
    "周末爱自己！",
    "周末奖励自己！",
    "周末吃顿好的！",
    "周末睡个懒觉！",
    
    # 社交类
    "约朋友出来玩！",
    "周末聚会走起！",
    "周末约饭！",
    "周末和朋友嗨！",
    "周末聊聊天！",
    "周末见朋友！",
    "周末社交时间！",
    "周末约局！",
    "周末派对！",
    "周末聚餐！",
    
    # 学习类（稍微正经一点）
    "周末学点新东西！",
    "周末看书去！",
    "周末提升自己！",
    "周末学习时间！",
    "周末充电！"
]

def load_config():
    """加载配置文件"""
    config_path = "feishu_config.json"
    
    if not os.path.exists(config_path):
        # 创建默认配置
        default_config = {
            "default_time": "17:55",
            "chats": {}
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    config_path = "feishu_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

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

def should_send_now(chat_id, config):
    """检查当前时间是否匹配该群的推送时间"""
    # 获取当前北京时间
    now = datetime.now()
    beijing_now = now + timedelta(hours=8)
    current_time = beijing_now.strftime("%H:%M")
    current_minute = beijing_now.strftime("%H:%M")
    
    # 检查该群是否有独立配置
    if chat_id in config["chats"]:
        chat_config = config["chats"][chat_id]
        if not chat_config.get("enabled", True):
            print(f"    ⏭️  该群已禁用")
            return False
        
        target_time = chat_config.get("time", config["default_time"])
    else:
        target_time = config["default_time"]
    
    print(f"    🕐 当前时间: {current_minute}, 目标时间: {target_time}")
    
    # 检查当前时间是否匹配目标时间（只匹配小时和分钟）
    if current_time == target_time:
        return True
    
    return False

def create_card(message, is_weekend):
    """创建飞书卡片"""
    
    # 根据工作日/周末选择不同的主题色和图标
    if is_weekend:
        title = "🎉 下班啦！快跑呀！！！"
        color = "green"
        icon = "🌞"
    else:
        title = "🌅 下班啦！快跑呀！！！"
        color = "blue"
        icon = "💼"
    
    # 获取当前时间（UTC）
    now = datetime.now()
    # 北京时间 = UTC + 8
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
                    "content": f"⏰ 发送时间：{beijing_time}",
                    "tag": "plain_text"
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
    code = data.get("code", -1)
    msg = data.get("msg", "unknown")
    
    if code == 0:
        print(f"    ✅ 发送成功")
        return True
    else:
        print(f"    ❌ 发送失败: 错误码={code}, 错误信息={msg}")
        return False

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
    
    print("📋 加载配置文件...")
    config = load_config()
    print(f"✅ 默认推送时间: {config['default_time']}")
    print(f"✅ 已配置的群数量: {len(config['chats'])}")
    
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
    
    print("📤 开始检查并发送消息...")
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_name = chat.get("name", "未命名")
        
        print(f"  检查群聊「{chat_name}」...")
        
        # 检查是否需要发送
        if should_send_now(chat_id, config):
            if send_message(token, chat_id, message, is_weekend_day):
                success_count += 1
            else:
                fail_count += 1
        else:
            skipped_count += 1
    
    print("=" * 32)
    print(f"✅ 成功发送: {success_count} 个群聊")
    print(f"❌ 发送失败: {fail_count} 个群聊")
    print(f"⏭️  跳过（时间未到）: {skipped_count} 个群聊")
    print("=" * 32)

if __name__ == "__main__":
    main()
