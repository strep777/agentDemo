#!/usr/bin/env python3
"""
测试修复后的聊天功能
"""

import requests
import json
import time

def test_chat_functionality():
    """测试聊天功能"""
    base_url = "http://localhost:3000/api"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev-token-12345'
    }
    
    print("🧪 开始测试聊天功能修复...")
    
    # 1. 测试获取对话列表
    print("\n1. 测试获取对话列表")
    try:
        response = requests.get(f"{base_url}/chat/conversations", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('data', [])
            print(f"✅ 获取对话列表成功: {len(conversations)} 个对话")
            
            if conversations:
                conversation_id = conversations[0]['id']
                print(f"🔍 使用对话ID进行测试: {conversation_id}")
                
                # 2. 测试获取消息
                print("\n2. 测试获取消息")
                response = requests.get(f"{base_url}/conversations/{conversation_id}/messages", 
                                      headers=headers)
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get('data', [])
                    print(f"✅ 获取消息成功: {len(messages)} 条消息")
                else:
                    print(f"❌ 获取消息失败: {response.text}")
            else:
                print("⚠️ 没有现有对话，跳过消息测试")
        else:
            print(f"❌ 获取对话列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 3. 测试创建新对话
    print("\n3. 测试创建新对话")
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
            
            # 4. 测试流式聊天
            print("\n4. 测试流式聊天")
            stream_data = {
                "conversation_id": conversation_id,
                "content": "你好，这是一个测试消息"
            }
            
            print("🔄 发送流式请求...")
            response = requests.post(f"{base_url}/chat/stream", 
                                   headers=headers, 
                                   json=stream_data,
                                   stream=True)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 流式请求成功，开始读取响应...")
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                if 'chunk' in data:
                                    print(f"📦 收到数据块: {data['chunk'][:50]}...")
                                elif 'done' in data:
                                    print("✅ 流式响应完成")
                                    break
                                elif 'error' in data:
                                    print(f"❌ 流式响应错误: {data['error']}")
                                    break
                            except json.JSONDecodeError:
                                print(f"⚠️ 无法解析JSON: {line_str}")
            else:
                print(f"❌ 流式请求失败: {response.text}")
        else:
            print(f"❌ 创建对话失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_chat_functionality() 