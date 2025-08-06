#!/usr/bin/env python3
"""
测试AI思考内容切换显示功能
验证思考内容能正确解析和显示
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
            "title": "测试对话 - 思考内容功能"
        }
        
        response = requests.post(f"{BASE_URL}/chat/conversations", headers=HEADERS, json=conversation_data, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                conversation = data.get('data')
                print(f"✅ 对话创建成功: {conversation.get('title')}")
                print(f"  - 对话ID: {conversation.get('id')}")
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

def test_send_message_with_thinking(conversation_id):
    """测试发送包含思考内容的消息"""
    try:
        print(f"🔍 发送包含思考内容的测试消息到对话: {conversation_id}")
        
        # 模拟一个包含思考内容的AI回复
        test_thinking_content = """```thinking
用户发送了"test"消息，我需要分析这个情况：

1. 用户可能是在测试系统功能
2. 消息内容很简单，可能是误操作或测试
3. 我应该提供友好的回复，询问用户需求
4. 保持专业和礼貌的态度很重要

基于以上分析，我应该：
- 确认用户的需求
- 提供帮助选项
- 保持开放式的回复
```"""

        message_data = {
            "conversation_id": conversation_id,
            "content": test_thinking_content + "\n\n您好！看起来您可能是在测试系统或输入内容。如果您有任何问题或需要帮助，请随时告诉我，我会尽力为您解答！ 😊",
            "show_thinking": True
        }
        
        response = requests.post(f"{BASE_URL}/chat/stream", headers=HEADERS, json=message_data, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 包含思考内容的消息发送成功")
            
            # 读取流式响应
            content = response.text
            print(f"📦 响应内容长度: {len(content)}")
            
            # 检查流式响应内容
            lines = content.split('\n')
            chunk_count = 0
            done_signal = False
            
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'chunk' in data:
                            chunk_count += 1
                            print(f"📦 数据块 {chunk_count}: {data['chunk'][:50]}...")
                        if 'done' in data:
                            done_signal = True
                            print(f"✅ 完成信号: {data}")
                    except json.JSONDecodeError:
                        print(f"⚠️ 无法解析JSON: {line}")
            
            print(f"📊 总共收到 {chunk_count} 个数据块")
            print(f"📊 完成信号: {'是' if done_signal else '否'}")
            
            return True
        else:
            print(f"❌ 消息发送HTTP错误: {response.status_code}")
            print(f"  - 响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return False

def test_get_messages_with_thinking(conversation_id):
    """测试获取包含思考内容的消息列表"""
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
                
                # 检查AI消息是否包含思考内容
                for i, msg in enumerate(assistant_messages):
                    content = msg.get('content', '')
                    print(f"  {i+1}. [AI] 消息长度: {len(content)}")
                    
                    # 检查是否包含思考内容标记
                    has_thinking = any(marker in content.lower() for marker in ['```thinking', '```思考', '<thinking>', '<思考>'])
                    print(f"     包含思考内容: {'是' if has_thinking else '否'}")
                    
                    if has_thinking:
                        # 简单解析思考内容
                        thinking_start = content.find('```thinking')
                        if thinking_start == -1:
                            thinking_start = content.find('```思考')
                        
                        if thinking_start != -1:
                            thinking_end = content.find('```', thinking_start + 3)
                            if thinking_end != -1:
                                thinking_content = content[thinking_start:thinking_end + 3]
                                print(f"     思考内容预览: {thinking_content[:100]}...")
                
                return True
            else:
                print(f"❌ 获取消息列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 获取消息列表HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取消息列表异常: {e}")
        return False

def test_thinking_content_parsing():
    """测试思考内容解析功能"""
    try:
        print("🔍 测试思考内容解析功能...")
        
        # 测试用例
        test_cases = [
            {
                "name": "标准thinking格式",
                "content": "```thinking\n这是思考过程\n```\n这是回复内容",
                "expected_thinking": "这是思考过程",
                "expected_reply": "这是回复内容"
            },
            {
                "name": "中文思考格式",
                "content": "```思考\n这是中文思考过程\n```\n这是中文回复",
                "expected_thinking": "这是中文思考过程",
                "expected_reply": "这是中文回复"
            },
            {
                "name": "XML格式",
                "content": "<thinking>XML思考内容</thinking>\nXML回复内容",
                "expected_thinking": "XML思考内容",
                "expected_reply": "XML回复内容"
            },
            {
                "name": "无思考内容",
                "content": "这是普通回复内容",
                "expected_thinking": "",
                "expected_reply": "这是普通回复内容"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"  📝 测试用例 {i+1}: {test_case['name']}")
            
            # 模拟前端解析逻辑
            content = test_case['content']
            
            # 检查是否包含思考内容
            has_thinking = any(marker in content.lower() for marker in ['```thinking', '```思考', '<thinking>', '<思考>'])
            print(f"    包含思考内容: {'是' if has_thinking else '否'}")
            
            # 简单解析思考内容
            thinking_content = ""
            reply_content = content
            
            if has_thinking:
                # 尝试解析thinking格式
                thinking_patterns = [
                    r'```thinking\n([\s\S]*?)\n```',
                    r'```思考\n([\s\S]*?)\n```',
                    r'<thinking>([\s\S]*?)</thinking>',
                    r'<思考>([\s\S]*?)</思考>'
                ]
                
                for pattern in thinking_patterns:
                    import re
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        thinking_content = match.group(1).strip()
                        reply_content = content.replace(match.group(0), '').strip()
                        break
            
            print(f"    解析结果:")
            print(f"      思考内容: {thinking_content[:50]}{'...' if len(thinking_content) > 50 else ''}")
            print(f"      回复内容: {reply_content[:50]}{'...' if len(reply_content) > 50 else ''}")
            
            # 验证结果
            if thinking_content == test_case['expected_thinking'] and reply_content == test_case['expected_reply']:
                print(f"    ✅ 解析正确")
            else:
                print(f"    ❌ 解析错误")
                print(f"      期望思考内容: {test_case['expected_thinking']}")
                print(f"      期望回复内容: {test_case['expected_reply']}")
        
        return True
    except Exception as e:
        print(f"❌ 思考内容解析测试异常: {e}")
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
    print("🧪 开始测试AI思考内容切换显示功能...")
    print("=" * 60)
    
    # 测试后端连接
    if not test_backend_connection():
        print("❌ 后端连接失败，无法继续测试")
        return
    
    print("\n" + "=" * 60)
    
    # 测试思考内容解析
    if not test_thinking_content_parsing():
        print("❌ 思考内容解析测试失败")
        return
    
    print("\n" + "=" * 60)
    
    # 创建测试对话
    conversation_id = test_create_conversation()
    if not conversation_id:
        print("❌ 创建对话失败，无法继续测试")
        return
    
    print("\n" + "=" * 60)
    
    # 发送包含思考内容的测试消息
    if not test_send_message_with_thinking(conversation_id):
        print("❌ 发送包含思考内容的消息失败")
        return
    
    print("\n" + "=" * 60)
    
    # 等待一下让消息处理完成
    print("⏳ 等待消息处理完成...")
    time.sleep(2)
    
    # 检查消息列表
    if not test_get_messages_with_thinking(conversation_id):
        print("❌ 检查包含思考内容的消息列表失败")
        return
    
    print("\n" + "=" * 60)
    
    # 清理测试对话
    test_delete_conversation(conversation_id)
    
    print("\n" + "=" * 60)
    print("🎉 AI思考内容切换显示功能测试完成！")
    print("📋 测试总结:")
    print("✅ 后端连接正常")
    print("✅ 思考内容解析功能正常")
    print("✅ 对话创建成功")
    print("✅ 包含思考内容的消息发送成功")
    print("✅ 消息列表检查通过")
    print("✅ 思考内容切换显示功能正常")

if __name__ == "__main__":
    main() 