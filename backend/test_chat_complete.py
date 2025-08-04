#!/usr/bin/env python3
"""
完整测试聊天功能修复
"""

import requests
import json
import time

def test_chat_complete():
    """完整测试聊天功能"""
    try:
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'  # 开发环境token
        }
        
        print("🔍 开始完整聊天功能测试...")
        
        # 1. 测试模型列表
        print("\n📋 1. 测试模型列表...")
        response = requests.get('http://localhost:3000/api/models', headers=headers)
        print(f"📊 模型列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ 模型列表获取成功，共 {len(models_data.get('data', {}).get('data', []))} 个模型")
            
            # 获取第一个模型用于测试
            models = models_data.get('data', {}).get('data', [])
            if models:
                test_model = models[0]
                print(f"📝 使用模型: {test_model.get('name', '未知')}")
            else:
                print("⚠️ 没有可用模型，创建测试模型...")
                # 创建测试模型
                model_data = {
                    'name': 'test-model',
                    'description': '测试模型',
                    'type': 'llm',
                    'provider': 'ollama',
                    'server_url': 'http://localhost:11434',
                    'parameters': '{"temperature": 0.7, "max_tokens": 1000}'
                }
                response = requests.post('http://localhost:3000/api/models', 
                                       headers=headers, json=model_data)
                if response.status_code == 201:
                    test_model = response.json()['data']
                    print(f"✅ 测试模型创建成功: {test_model.get('name')}")
                else:
                    print(f"❌ 测试模型创建失败: {response.text}")
                    return
        else:
            print(f"❌ 模型列表获取失败: {response.text}")
            return
        
        # 2. 测试创建对话
        print("\n💬 2. 测试创建对话...")
        conversation_data = {
            'type': 'model',
            'model_id': test_model['id'],
            'title': '测试对话'
        }
        response = requests.post('http://localhost:3000/api/chat/conversations', 
                               headers=headers, json=conversation_data)
        print(f"📊 创建对话响应状态码: {response.status_code}")
        if response.status_code == 201:
            conversation = response.json()['data']
            conversation_id = conversation['id']
            print(f"✅ 对话创建成功: {conversation['title']}")
            
            # 3. 测试发送消息
            print("\n📤 3. 测试发送消息...")
            message_data = {
                'conversation_id': conversation_id,
                'content': '你好，请介绍一下自己'
            }
            
            # 使用流式接口
            print("🔄 使用流式接口发送消息...")
            response = requests.post('http://localhost:3000/api/chat/stream', 
                                   headers=headers, json=message_data, stream=True)
            print(f"📊 流式响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 流式消息发送成功")
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
                print(f"❌ 流式消息发送失败: {response.text}")
            
            # 4. 测试获取消息列表
            print("\n📋 4. 测试获取消息列表...")
            response = requests.get(f'http://localhost:3000/api/chat/conversations/{conversation_id}/messages', 
                                  headers=headers)
            print(f"📊 获取消息响应状态码: {response.status_code}")
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get('data', [])
                print(f"✅ 获取消息成功，共 {len(messages)} 条消息")
                for i, msg in enumerate(messages):
                    print(f"  {i+1}. [{msg.get('type', 'unknown')}] {msg.get('content', '')[:50]}...")
            else:
                print(f"❌ 获取消息失败: {response.text}")
                
        else:
            print(f"❌ 对话创建失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保后端服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_chat_complete() 