#!/usr/bin/env python3
"""
测试聊天功能修复
"""

import requests
import json

def test_chat_fix():
    """测试聊天功能修复"""
    try:
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'  # 开发环境token
        }
        
        # 1. 测试模型列表
        print("🔍 测试模型列表...")
        response = requests.get('http://localhost:3000/api/models', headers=headers)
        print(f"📊 模型列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 模型列表获取成功")
        else:
            print(f"❌ 模型列表获取失败: {response.text}")
        
        # 2. 测试创建对话
        print("\n🔍 测试创建对话...")
        conversation_data = {
            'type': 'model',
            'model_id': 'test-model-id',  # 需要有效的模型ID
            'title': '测试对话'
        }
        response = requests.post('http://localhost:3000/api/chat/conversations', 
                               headers=headers, json=conversation_data)
        print(f"📊 创建对话响应状态码: {response.status_code}")
        if response.status_code == 201:
            print("✅ 对话创建成功")
            conversation_id = response.json()['data']['id']
            
            # 3. 测试发送消息
            print("\n🔍 测试发送消息...")
            message_data = {
                'conversation_id': conversation_id,
                'content': '你好，请介绍一下自己'
            }
            response = requests.post('http://localhost:3000/api/chat/stream', 
                                   headers=headers, json=message_data)
            print(f"📊 发送消息响应状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 消息发送成功")
                print("📋 流式响应内容:")
                print(response.text)
            else:
                print(f"❌ 消息发送失败: {response.text}")
        else:
            print(f"❌ 对话创建失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保后端服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

if __name__ == '__main__':
    test_chat_fix() 