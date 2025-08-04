#!/usr/bin/env python3
"""
测试模型创建功能
"""

import requests
import json

def test_model_creation():
    """测试模型创建 API"""
    
    # 测试 URL
    url = "http://localhost:3000/api/models"
    
    # 测试数据
    data = {
        'name': 'test-model',
        'description': '测试模型',
        'type': 'llm',
        'provider': 'ollama',
        'server_url': 'http://172.16.156.100:11434',
        'parameters': {}
    }
    
    # 请求头
    headers = {
        'Authorization': 'Bearer dev-token-12345',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 测试模型创建...")
        print(f"📤 请求 URL: {url}")
        print(f"📤 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"📤 请求头: {headers}")
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 请求成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ 请求超时: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_model_creation() 