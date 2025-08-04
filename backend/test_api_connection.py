#!/usr/bin/env python3
"""
测试后端API连接
"""

import requests
import json

def test_api_connection():
    """测试API连接"""
    base_url = "http://localhost:3000"
    
    # 测试健康检查
    try:
        print("🔍 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"📊 健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 健康检查成功")
        else:
            print(f"❌ 健康检查失败: {response.text}")
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False
    
    # 测试聊天API
    try:
        print("\n🔍 测试聊天API...")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'
        }
        
        # 测试获取对话列表
        response = requests.get(f"{base_url}/api/chat/conversations", headers=headers, timeout=5)
        print(f"📊 对话列表状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 对话列表API正常")
        else:
            print(f"❌ 对话列表API失败: {response.text}")
    except Exception as e:
        print(f"❌ 聊天API异常: {str(e)}")
        return False
    
    # 测试流式聊天API
    try:
        print("\n🔍 测试流式聊天API...")
        data = {
            'conversation_id': 'test_id',
            'content': 'test message'
        }
        
        response = requests.post(f"{base_url}/api/chat/stream", headers=headers, json=data, timeout=5)
        print(f"📊 流式聊天状态码: {response.status_code}")
        if response.status_code in [200, 400, 404]:  # 400/404是预期的，因为test_id无效
            print("✅ 流式聊天API可访问")
        else:
            print(f"❌ 流式聊天API异常: {response.text}")
    except Exception as e:
        print(f"❌ 流式聊天API异常: {str(e)}")
        return False
    
    print("\n✅ API连接测试完成")
    return True

if __name__ == "__main__":
    test_api_connection() 