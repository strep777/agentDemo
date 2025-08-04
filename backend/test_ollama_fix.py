#!/usr/bin/env python3
"""
测试 Ollama 健康检查修复
"""

import requests
import json

def test_ollama_health():
    """测试 Ollama 健康检查 API"""
    
    # 测试 URL
    url = "http://localhost:3000/api/models/ollama/health"
    
    # 测试参数
    params = {
        'server_url': 'http://172.16.156.100:11434'
    }
    
    # 请求头
    headers = {
        'Authorization': 'Bearer dev-token-12345',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 测试 Ollama 健康检查...")
        print(f"📤 请求 URL: {url}")
        print(f"📤 请求参数: {params}")
        print(f"📤 请求头: {headers}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
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
    test_ollama_health() 