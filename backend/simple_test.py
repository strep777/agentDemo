#!/usr/bin/env python3
"""
简单语法测试
"""

try:
    # 测试基本语法
    exec(open('app.py').read())
    print("✅ 语法检查通过")
except SyntaxError as e:
    print(f"❌ 语法错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}") 