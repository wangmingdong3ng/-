#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

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

def send_message(token, chat_id, message):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "chat_id"}
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": message})
    }
    
    response = requests.post(url, headers=headers, params=params, json=payload)
    data = response.json()
    
    return data.get("code") == 0

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
    
    print("📤 开始发送消息...")
    
    success_count = 0
    fail_count = 0
    
    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_name = chat.get("name", "未命名")
        
        message = "🌅 下班快乐！"
        
        print(f"  发送到「{chat_name}」...")
        
        if send_message(token, chat_id, message):
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
