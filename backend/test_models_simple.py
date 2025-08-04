#!/usr/bin/env python3
"""
简单测试models端点
"""

import requests
import json

def test_models_endpoint():
    """测试GET /api/models端点"""
    try:
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer dev-token-12345'  # 开发环境token
        }
        
        # 发送请求
        url = 'http://localhost:3000/api/models'
        print(f"🔍 测试端点: {url}")
        
        response = requests.get(url, headers=headers)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            data = response.json()
            print(f"📋 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 错误内容: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保后端服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

if __name__ == '__main__':
    test_models_endpoint() 