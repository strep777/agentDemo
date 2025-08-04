#!/usr/bin/env python3
"""
测试聊天功能修复
"""

import requests
import json
import time

def test_chat_fixes():
    """测试聊天功能修复"""
    try:
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'  # 开发环境token
        }
        
        print("🔍 开始测试聊天功能修复...")
        
        # 1. 测试获取对话列表
        print("\n📋 1. 测试获取对话列表...")
        response = requests.get('http://localhost:3000/api/chat/conversations', headers=headers)
        print(f"📊 对话列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            conversations_data = response.json()
            conversations = conversations_data.get('data', {}).get('data', [])
            print(f"✅ 对话列表获取成功，共 {len(conversations)} 个对话")
            
            if conversations:
                conversation_id = conversations[0]['id']
                print(f"📝 使用对话ID: {conversation_id}")
                
                # 2. 测试获取消息列表
                print("\n📋 2. 测试获取消息列表...")
                response = requests.get(f'http://localhost:3000/api/chat/conversations/{conversation_id}/messages', headers=headers)
                print(f"📊 消息列表响应状态码: {response.status_code}")
                if response.status_code == 200:
                    messages_data = response.json()
                    messages = messages_data.get('data', [])
                    print(f"✅ 消息列表获取成功，共 {len(messages)} 条消息")
                else:
                    print(f"❌ 消息列表获取失败: {response.text}")
                    return
                
                # 3. 测试发送消息
                print("\n📤 3. 测试发送消息...")
                message_data = {
                    'conversation_id': conversation_id,
                    'content': '你好，这是一个测试消息'
                }
                response = requests.post('http://localhost:3000/api/chat/send', headers=headers, json=message_data)
                print(f"📊 发送消息响应状态码: {response.status_code}")
                if response.status_code == 200:
                    print("✅ 消息发送成功")
                else:
                    print(f"❌ 消息发送失败: {response.text}")
                
                # 4. 测试流式聊天
                print("\n🔄 4. 测试流式聊天...")
                stream_data = {
                    'conversation_id': conversation_id,
                    'content': '你好，请介绍一下自己'
                }
                response = requests.post('http://localhost:3000/api/chat/stream', headers=headers, json=stream_data, stream=True)
                print(f"📊 流式聊天响应状态码: {response.status_code}")
                if response.status_code == 200:
                    print("✅ 流式聊天开始成功")
                    print("📋 流式响应内容:")
                    
                    # 读取流式响应
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunk_text = chunk.decode('utf-8')
                            print(f"📦 收到数据块: {chunk_text[:100]}...")
                            
                            # 解析SSE格式
                            lines = chunk_text.split('\n')
                            for line in lines:
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])
                                        if 'chunk' in data:
                                            print(f"💭 AI回复片段: {data['chunk']}")
                                        if 'done' in data and data['done']:
                                            print("✅ 流式传输完成")
                                            break
                                    except json.JSONDecodeError:
                                        print(f"⚠️ 无法解析JSON: {line}")
                else:
                    print(f"❌ 流式聊天失败: {response.text}")
                
                # 5. 测试删除对话
                print("\n🗑️ 5. 测试删除对话...")
                response = requests.delete(f'http://localhost:3000/api/chat/conversations/{conversation_id}', headers=headers)
                print(f"📊 删除对话响应状态码: {response.status_code}")
                if response.status_code == 200:
                    print("✅ 对话删除成功")
                else:
                    print(f"❌ 对话删除失败: {response.text}")
            else:
                print("⚠️ 没有可用对话，跳过后续测试")
        else:
            print(f"❌ 对话列表获取失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保后端服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_chat_fixes() 