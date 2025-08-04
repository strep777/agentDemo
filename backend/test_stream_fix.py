#!/usr/bin/env python3
"""
测试流式聊天修复
"""

import requests
import json

def test_stream_chat():
    """测试流式聊天"""
    try:
        print("🔍 测试流式聊天...")
        
        # 首先创建一个对话
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'
        }
        
        # 创建对话
        conversation_data = {
            'type': 'model',
            'title': '测试对话',
            'model_id': '688c725bc23732c6dcabcd2e'
        }
        
        response = requests.post('http://localhost:3000/api/chat/conversations', 
                               headers=headers, json=conversation_data)
        
        if response.status_code != 201:
            print(f"❌ 创建对话失败: {response.status_code}")
            return False
            
        conversation_id = response.json()['data']['id']
        print(f"✅ 创建对话成功: {conversation_id}")
        
        # 测试流式聊天
        stream_data = {
            'conversation_id': conversation_id,
            'content': '你好，请简单介绍一下你自己'
        }
        
        print("🔄 开始流式聊天测试...")
        response = requests.post('http://localhost:3000/api/chat/stream', 
                               headers=headers, json=stream_data, stream=True, timeout=30)
        
        print(f"📊 流式响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 流式聊天连接成功")
            
            # 读取流式响应
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if 'chunk' in data:
                                print(f"📦 收到数据块: {data['chunk'][:50]}...")
                            if data.get('done'):
                                print("✅ 流式聊天完成")
                                break
                        except json.JSONDecodeError:
                            continue
            return True
        else:
            print(f"❌ 流式聊天失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    test_stream_chat() 