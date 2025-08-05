#!/usr/bin/env python3
"""
测试聊天页面消息重复发送修复
验证用户消息不会发送两次
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:5000/api"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dev-token-12345"
}

def test_backend_connection():
    """测试后端连接"""
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS, timeout=5)
        print(f"✅ 后端连接正常: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_create_conversation():
    """测试创建对话"""
    try:
        print("🔍 创建测试对话...")
        
        conversation_data = {
            "type": "model",
            "title": "测试对话 - 消息重复修复"
        }
        
        response = requests.post(f"{BASE_URL}/chat/conversations", headers=HEADERS, json=conversation_data, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                conversation = data.get('data')
                print(f"✅ 对话创建成功: {conversation.get('title')}")
                print(f"  - 对话ID: {conversation.get('id')}")
                print(f"  - 对话类型: {conversation.get('type')}")
                return conversation.get('id')
            else:
                print(f"❌ 对话创建失败: {data.get('message')}")
                return None
        else:
            print(f"❌ 对话创建HTTP错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 创建对话异常: {e}")
        return None

def test_send_message(conversation_id):
    """测试发送消息"""
    try:
        print(f"🔍 发送测试消息到对话: {conversation_id}")
        
        message_data = {
            "conversation_id": conversation_id,
            "content": "Hello, this is a test message to check for duplicate sending.",
            "show_thinking": False
        }
        
        response = requests.post(f"{BASE_URL}/chat/stream", headers=HEADERS, json=message_data, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 流式消息发送成功")
            
            # 读取流式响应
            content = response.text
            print(f"📦 响应内容长度: {len(content)}")
            print(f"📦 响应内容预览: {content[:200]}...")
            
            # 检查是否有重复的用户消息
            lines = content.split('\n')
            user_message_count = 0
            assistant_message_count = 0
            
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'chunk' in data:
                            print(f"📦 数据块: {data['chunk'][:50]}...")
                        if 'done' in data:
                            print(f"✅ 完成信号: {data}")
                    except json.JSONDecodeError:
                        print(f"⚠️ 无法解析JSON: {line}")
            
            return True
        else:
            print(f"❌ 消息发送HTTP错误: {response.status_code}")
            print(f"  - 响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return False

def test_get_messages(conversation_id):
    """测试获取消息列表"""
    try:
        print(f"🔍 获取对话消息: {conversation_id}")
        
        response = requests.get(f"{BASE_URL}/chat/conversations/{conversation_id}/messages", headers=HEADERS, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                messages = data.get('data', {}).get('data', [])
                print(f"✅ 获取消息列表成功: {len(messages)} 条消息")
                
                # 检查消息类型分布
                user_messages = [m for m in messages if m.get('type') == 'user']
                assistant_messages = [m for m in messages if m.get('type') == 'assistant']
                
                print(f"  - 用户消息数量: {len(user_messages)}")
                print(f"  - AI消息数量: {len(assistant_messages)}")
                
                # 检查是否有重复的用户消息
                user_contents = [m.get('content', '') for m in user_messages]
                unique_contents = set(user_contents)
                
                if len(user_contents) == len(unique_contents):
                    print("✅ 没有发现重复的用户消息")
                    return True
                else:
                    print("❌ 发现重复的用户消息!")
                    print(f"  - 总消息数: {len(user_contents)}")
                    print(f"  - 唯一消息数: {len(unique_contents)}")
                    return False
            else:
                print(f"❌ 获取消息列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取消息列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取消息列表异常: {e}")
        return False

def test_delete_conversation(conversation_id):
    """测试删除对话"""
    try:
        print(f"🔍 删除测试对话: {conversation_id}")
        
        response = requests.delete(f"{BASE_URL}/chat/conversations/{conversation_id}", headers=HEADERS, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 对话删除成功")
                return True
            else:
                print(f"❌ 对话删除失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 对话删除HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除对话异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试聊天页面消息重复发送修复...")
    print("=" * 60)
    
    # 测试后端连接
    if not test_backend_connection():
        print("❌ 后端连接失败，无法继续测试")
        return
    
    print("\n" + "=" * 60)
    
    # 创建测试对话
    conversation_id = test_create_conversation()
    if not conversation_id:
        print("❌ 创建对话失败，无法继续测试")
        return
    
    print("\n" + "=" * 60)
    
    # 发送测试消息
    if not test_send_message(conversation_id):
        print("❌ 发送消息失败")
        return
    
    print("\n" + "=" * 60)
    
    # 等待一下让消息处理完成
    print("⏳ 等待消息处理完成...")
    time.sleep(2)
    
    # 检查消息列表
    if not test_get_messages(conversation_id):
        print("❌ 检查消息列表失败")
        return
    
    print("\n" + "=" * 60)
    
    # 清理测试对话
    test_delete_conversation(conversation_id)
    
    print("\n" + "=" * 60)
    print("🎉 聊天页面消息重复发送修复测试完成！")
    print("📋 测试总结:")
    print("✅ 后端连接正常")
    print("✅ 对话创建成功")
    print("✅ 消息发送成功")
    print("✅ 消息列表检查通过")
    print("✅ 没有发现重复的用户消息")

if __name__ == "__main__":
    main() 