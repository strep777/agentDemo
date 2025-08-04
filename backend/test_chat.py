#!/usr/bin/env python3
"""
测试聊天功能
"""

import requests
import json

def test_chat_endpoints():
    """测试聊天相关端点"""
    base_url = "http://localhost:3000/api"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev-token-12345'
    }
    
    print("🧪 开始测试聊天功能...")
    
    # 1. 测试获取对话列表
    print("\n1. 测试获取对话列表")
    try:
        response = requests.get(f"{base_url}/chat/conversations", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取对话列表成功: {len(data.get('data', []))} 个对话")
        else:
            print(f"❌ 获取对话列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 2. 测试创建对话
    print("\n2. 测试创建对话")
    try:
        create_data = {
            "type": "model",
            "model_id": "688c725bc23732c6dcabcd2e",
            "title": "测试对话"
        }
        response = requests.post(f"{base_url}/chat/conversations", 
                               headers=headers, 
                               json=create_data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            conversation_id = data.get('data', {}).get('id')
            print(f"✅ 创建对话成功: {conversation_id}")
            
            # 3. 测试获取消息
            print("\n3. 测试获取消息")
            response = requests.get(f"{base_url}/conversations/{conversation_id}/messages", 
                                  headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取消息成功: {len(data.get('data', []))} 条消息")
            else:
                print(f"❌ 获取消息失败: {response.text}")
                
        else:
            print(f"❌ 创建对话失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_chat_endpoints() 