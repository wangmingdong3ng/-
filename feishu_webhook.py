#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# 加载配置文件
def load_config():
    config_path = "feishu_config.json"
    
    if not os.path.exists(config_path):
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
        return None
    
    return data.get("tenant_access_token")

def send_message(token, receive_id, content, msg_type="interactive"):
    """发送消息到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "chat_id"}
    
    payload = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": json.dumps(content) if msg_type == "interactive" else content
    }
    
    response = requests.post(url, headers=headers, params=params, json=payload)
    data = response.json()
    
    return data.get("code") == 0

def create_setting_card(chat_id, current_time):
    """创建设置推送时间的卡片"""
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "content": "⏰ 推送时间设置",
                "tag": "plain_text"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"当前推送时间：{current_time}",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "📝 设置推送时间",
                            "tag": "plain_text"
                        },
                        "type": "primary",
                        "value": {
                            "action": "set_time",
                            "chat_id": chat_id
                        }
                    },
                    {
                        "tag": "button",
                        "text": {
                            "content": "♻️ 恢复默认",
                            "tag": "plain_text"
                        },
                        "type": "default",
                        "value": {
                            "action": "reset_time",
                            "chat_id": chat_id
                        }
                    }
                ]
            }
        ]
    }
    
    return card

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理飞书 Webhook 请求"""
    try:
        data = request.json
        
        # 验证请求
        if data.get("type") == "url_verification":
            # URL 验证请求
            return jsonify({
                "challenge": data.get("challenge")
            })
        
        # 处理消息事件
        if data.get("header", {}).get("event_type") == "im.message.receive_v1":
            event = data.get("event", {})
            
            # 检查是否是 @机器人
            mentions = event.get("message", {}).get("mentions", [])
            if not mentions:
                return jsonify({"code": 0})
            
            # 获取群聊 ID
            chat_id = event.get("message", {}).get("chat_id")
            if not chat_id:
                return jsonify({"code": 0})
            
            # 获取配置
            config = load_config()
            
            # 获取当前配置的时间
            if chat_id in config["chats"]:
                current_time = config["chats"][chat_id].get("time", config["default_time"])
            else:
                current_time = config["default_time"]
            
            # 获取 Token
            app_id = os.environ.get("FEISHU_APP_ID")
            app_secret = os.environ.get("FEISHU_APP_SECRET")
            token = get_token(app_id, app_secret)
            
            if not token:
                return jsonify({"code": 0})
            
            # 发送设置卡片
            card = create_setting_card(chat_id, current_time)
            send_message(token, chat_id, card)
            
            return jsonify({"code": 0})
        
        # 处理卡片交互事件
        if data.get("header", {}).get("event_type") == "application.bot.action_v6":
            event = data.get("event", {})
            action = event.get("action", {})
            value = action.get("value", {})
            
            action_type = value.get("action")
            chat_id = value.get("chat_id")
            
            if not chat_id:
                return jsonify({"code": 0})
            
            # 获取 Token
            app_id = os.environ.get("FEISHU_APP_ID")
            app_secret = os.environ.get("FEISHU_APP_SECRET")
            token = get_token(app_id, app_secret)
            
            if not token:
                return jsonify({"code": 0})
            
            if action_type == "set_time":
                # 打开对话框，让用户选择时间
                open_data = {
                    "token": {
                        "title": "设置推送时间",
                        "subtitle": "请选择您希望接收下班祝福的时间",
                        "body": {
                            "tag": "form",
                            "value": {
                                "chat_id": chat_id
                            }
                        }
                    }
                }
                
                # 这里需要使用飞书的 Open Dialog API
                # 简化处理，直接发送文本消息提示用户
                send_message(token, chat_id, {
                    "text": "⚠️ 对话框功能需要配置飞书 Open Dialog API\n\n请回复格式：设置时间 18:00\n\n例如：设置时间 18:00"
                }, "text")
                
            elif action_type == "reset_time":
                # 恢复默认时间
                config = load_config()
                if chat_id in config["chats"]:
                    config["chats"][chat_id]["time"] = config["default_time"]
                    config["chats"][chat_id]["enabled"] = True
                    save_config(config)
                
                # 发送成功消息
                card = create_setting_card(chat_id, config["default_time"])
                send_message(token, chat_id, card)
                
                send_message(token, chat_id, {
                    "text": "✅ 已恢复默认推送时间：17:55"
                }, "text")
            
            return jsonify({"code": 0})
        
        return jsonify({"code": 0})
    
    except Exception as e:
        print(f"❌ 处理 Webhook 请求出错: {e}")
        return jsonify({"code": 0})

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
