import requests
import json

def test_create_conversation():
    """测试创建对话功能"""
    url = "http://localhost:5000/api/chat/conversations"
    
    # 测试数据
    data = {
        "type": "model",
        "model_id": "507f1f77bcf86cd799439011",  # 示例 ObjectId
        "title": "测试对话"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dev-token-12345"
    }
    
    try:
        print("🧪 测试创建对话...")
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ 对话创建成功！")
            response_data = response.json()
            print(f"📝 创建的对话: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 对话创建失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_create_conversation() 