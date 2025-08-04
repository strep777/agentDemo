#!/usr/bin/env python3
"""
语法测试脚本
用于验证后端代码的语法是否正确
"""

try:
    import app
    print("✅ 语法检查通过")
    print("✅ 所有导入成功")
except SyntaxError as e:
    print(f"❌ 语法错误: {e}")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}") 