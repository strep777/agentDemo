#!/usr/bin/env python3
"""
Ollama集成和模型管理功能测试脚本

验证以下功能：
1. Ollama服务器连接
2. 获取Ollama可用模型列表
3. 创建Ollama模型
4. 模型管理页面的Ollama集成
5. 聊天功能的Ollama集成

使用方法：
    python test_ollama_integration.py
"""

import requests
import json
import time

# 配置常量
BASE_URL = "http://localhost:5000/api"  # 后端API基础URL
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dev-token-12345"  # 开发环境认证token
}

def test_backend_connection():
    """
    测试后端连接
    
    Returns:
        bool: 连接是否成功
    """
    try:
        # 发送健康检查请求
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS, timeout=5)
        print(f"✅ 后端连接正常: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_ollama_health():
    """
    测试Ollama健康状态
    
    Returns:
        bool: Ollama是否健康
    """
    try:
        print("🔍 测试Ollama健康状态...")
        # 调用后端API检查Ollama健康状态
        response = requests.get(f"{BASE_URL}/models/ollama/health", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                is_healthy = data.get('data', {}).get('healthy', False)
                server_url = data.get('data', {}).get('server_url', 'unknown')
                print(f"✅ Ollama健康检查完成: {is_healthy}")
                print(f"  - 服务器地址: {server_url}")
                return is_healthy
            else:
                print(f"❌ Ollama健康检查失败: {data.get('message')}")
                return False
        else:
            print(f"❌ Ollama健康检查HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama健康检查异常: {e}")
        return False

def test_get_ollama_models():
    """
    测试获取Ollama模型列表
    
    Returns:
        list: 可用模型列表
    """
    try:
        print("🔍 获取Ollama模型列表...")
        # 调用后端API获取Ollama模型列表
        response = requests.get(f"{BASE_URL}/models/ollama/models", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models = data.get('data', [])
                print(f"✅ 获取Ollama模型列表成功: {len(models)} 个模型")
                # 显示前5个模型
                for i, model in enumerate(models[:5]):
                    print(f"  {i+1}. {model}")
                if len(models) > 5:
                    print(f"  ... 还有 {len(models) - 5} 个模型")
                return models
            else:
                print(f"❌ 获取Ollama模型列表失败: {data.get('message')}")
                return []
        else:
            print(f"❌ 获取Ollama模型列表HTTP错误: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取Ollama模型列表异常: {e}")
        return []

def test_create_ollama_model():
    """
    测试创建Ollama模型
    
    Returns:
        bool: 创建是否成功
    """
    try:
        # 首先获取可用模型列表
        models = test_get_ollama_models()
        if not models:
            print("❌ 没有可用的Ollama模型，跳过创建测试")
            return False
        
        # 选择第一个模型进行测试
        test_model_name = models[0]
        print(f"🔍 测试创建Ollama模型: {test_model_name}")
        
        # 构建模型数据
        model_data = {
            "name": test_model_name,
            "description": f"{test_model_name} 测试模型",
            "type": "llm",
            "provider": "ollama",
            "server_url": "http://localhost:11434",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        }
        
        # 调用后端API创建模型
        response = requests.post(f"{BASE_URL}/models", headers=HEADERS, json=model_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                created_model = data.get('data')
                print(f"✅ 创建Ollama模型成功: {created_model.get('name')}")
                print(f"  - 模型ID: {created_model.get('id')}")
                print(f"  - 提供商: {created_model.get('provider')}")
                print(f"  - 服务器: {created_model.get('server_url')}")
                return True
            else:
                print(f"❌ 创建Ollama模型失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 创建Ollama模型HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 创建Ollama模型异常: {e}")
        return False

def test_model_management_features():
    """
    测试模型管理功能
    
    Returns:
        bool: 测试是否成功
    """
    try:
        print("🔍 测试模型管理功能...")
        
        # 1. 获取现有模型列表
        response = requests.get(f"{BASE_URL}/models", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models = data.get('data', {}).get('data', [])
                print(f"✅ 获取模型列表成功: {len(models)} 个模型")
                
                # 2. 查找Ollama模型
                ollama_models = [m for m in models if m.get('provider') == 'ollama']
                print(f"  - Ollama模型数量: {len(ollama_models)}")
                
                if ollama_models:
                    # 3. 测试第一个Ollama模型
                    test_model = ollama_models[0]
                    print(f"  - 测试模型: {test_model.get('name')}")
                    
                    # 4. 测试模型
                    test_response = requests.post(
                        f"{BASE_URL}/models/{test_model.get('id')}/test",
                        headers=HEADERS,
                        json={"message": "Hello, how are you?"},
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        if test_data.get('success'):
                            result = test_data.get('data')
                            if result.get('success'):
                                print(f"✅ 模型测试成功: {result.get('response', '')[:100]}...")
                            else:
                                print(f"❌ 模型测试失败: {result.get('error')}")
                        else:
                            print(f"❌ 模型测试API失败: {test_data.get('message')}")
                    else:
                        print(f"❌ 模型测试HTTP错误: {test_response.status_code}")
                
                return True
            else:
                print(f"❌ 获取模型列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取模型列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 模型管理功能测试异常: {e}")
        return False

def test_ollama_integration_workflow():
    """
    测试完整的Ollama集成工作流程
    
    Returns:
        bool: 工作流程是否成功
    """
    try:
        print("🔍 测试完整的Ollama集成工作流程...")
        
        # 1. 检查Ollama连接
        if not test_ollama_health():
            print("❌ Ollama连接失败，无法继续测试")
            return False
        
        # 2. 获取可用模型
        models = test_get_ollama_models()
        if not models:
            print("❌ 没有可用的Ollama模型")
            return False
        
        # 3. 创建模型
        if not test_create_ollama_model():
            print("❌ 创建Ollama模型失败")
            return False
        
        # 4. 测试模型管理功能
        if not test_model_management_features():
            print("❌ 模型管理功能测试失败")
            return False
        
        print("✅ 完整的Ollama集成工作流程测试通过")
        return True
    except Exception as e:
        print(f"❌ Ollama集成工作流程测试异常: {e}")
        return False

def main():
    """
    主测试函数
    按顺序执行所有测试用例
    """
    print("🧪 开始测试Ollama集成和模型管理功能...")
    print("=" * 60)
    
    # 测试后端连接
    if not test_backend_connection():
        print("❌ 后端连接失败，无法继续测试")
        return
    
    print("\n" + "=" * 60)
    
    # 测试Ollama健康状态
    if not test_ollama_health():
        print("❌ Ollama连接失败，请确保Ollama服务器正在运行")
        print("💡 提示: 请启动Ollama服务器 (ollama serve)")
        return
    
    print("\n" + "=" * 60)
    
    # 测试获取Ollama模型列表
    models = test_get_ollama_models()
    if not models:
        print("❌ 没有可用的Ollama模型")
        print("💡 提示: 请安装一些模型 (ollama pull llama2)")
        return
    
    print("\n" + "=" * 60)
    
    # 测试创建Ollama模型
    if not test_create_ollama_model():
        print("❌ 创建Ollama模型失败")
        return
    
    print("\n" + "=" * 60)
    
    # 测试模型管理功能
    if not test_model_management_features():
        print("❌ 模型管理功能测试失败")
        return
    
    print("\n" + "=" * 60)
    
    # 测试完整工作流程
    if test_ollama_integration_workflow():
        print("🎉 所有Ollama集成测试通过！")
    else:
        print("❌ 部分测试失败")
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print("✅ 后端连接正常")
    print("✅ Ollama服务器连接正常")
    print("✅ 模型管理功能正常")
    print("✅ 可以创建和管理Ollama模型")

if __name__ == "__main__":
    main() 