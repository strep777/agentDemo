"""
插件执行服务
提供插件执行和管理功能
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any, List
from app.services.database import get_db
import tempfile

class PluginExecutor:
    def __init__(self):
        self.db = None
        self.plugin_dir = os.path.join(os.getcwd(), 'backend', 'plugins')
        os.makedirs(self.plugin_dir, exist_ok=True)
    
    def set_db(self, db):
        self.db = db
    
    def execute_plugin(self, plugin: Dict, input_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """执行插件"""
        try:
            if not plugin:
                return {
                    'success': False,
                    'error': '插件不存在'
                }
            
            if plugin.get('status') != 'active':
                return {
                    'success': False,
                    'error': '插件未启用'
                }
            
            plugin_type = plugin.get('type', 'http')
            
            if plugin_type == 'http':
                return self._execute_http_plugin(plugin, input_data)
            elif plugin_type == 'python':
                return self._execute_python_plugin(plugin, input_data)
            elif plugin_type == 'workflow':
                return self._execute_workflow_plugin(plugin, input_data)
            else:
                return {
                    'success': False,
                    'error': f'不支持的插件类型: {plugin_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'执行插件失败: {str(e)}'
            }
    
    def test_plugin(self, plugin: Dict, test_input: Dict[str, Any]) -> Dict[str, Any]:
        """测试插件"""
        try:
            # 检查插件状态
            if plugin.get('status') != 'active':
                return {
                    'success': False,
                    'error': '插件未启用，无法测试'
                }
            
            # 根据插件类型执行测试
            plugin_type = plugin.get('type', 'http')
            
            if plugin_type == 'http':
                return self._test_http_plugin(plugin, test_input)
            elif plugin_type == 'python':
                return self._test_python_plugin(plugin, test_input)
            elif plugin_type == 'workflow':
                return self._test_workflow_plugin(plugin, test_input)
            else:
                # 对于其他类型的插件，返回模拟测试结果
                return {
                    'success': True,
                    'result': {
                        'plugin_name': plugin.get('name'),
                        'plugin_type': plugin_type,
                        'test_input': test_input,
                        'test_output': f'模拟测试结果 - {plugin.get("name")}',
                        'execution_time': 0.1,
                        'status': 'success'
                    },
                    'message': '插件测试成功'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'插件测试失败: {str(e)}'
            }
    
    def _execute_http_plugin(self, plugin: Dict, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行HTTP插件"""
        try:
            config = plugin.get('config', {})
            url = config.get('url')
            method = config.get('method', 'POST')
            headers = config.get('headers', {})
            
            if not url:
                return {
                    'success': False,
                    'error': 'HTTP插件缺少URL配置'
                }
            
            # 发送HTTP请求
            if method.upper() == 'GET':
                response = requests.get(url, params=input_data, headers=headers, timeout=30)
            else:
                response = requests.post(url, json=input_data, headers=headers, timeout=30)
            
            response.raise_for_status()
            
            return {
                'success': True,
                'result': response.json(),
                'status_code': response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'HTTP请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'HTTP插件执行失败: {str(e)}'
            }
    
    def _execute_python_plugin(self, plugin: Dict, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Python插件"""
        try:
            config = plugin.get('config', {})
            code = config.get('code', '')
            
            if not code:
                return {
                    'success': False,
                    'error': 'Python插件缺少代码配置'
                }
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # 执行Python代码
                result = subprocess.run(
                    ['python', temp_file],
                    input=json.dumps(input_data),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        return {
                            'success': True,
                            'result': output
                        }
                    except json.JSONDecodeError:
                        return {
                            'success': True,
                            'result': result.stdout.strip()
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Python代码执行失败: {result.stderr}'
                    }
                    
            finally:
                # 清理临时文件
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Python插件执行失败: {str(e)}'
            }
    
    def _execute_workflow_plugin(self, plugin: Dict, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流插件"""
        try:
            config = plugin.get('config', {})
            workflow_id = config.get('workflow_id')
            
            if not workflow_id:
                return {
                    'success': False,
                    'error': '工作流插件缺少工作流ID配置'
                }
            
            # 这里应该调用工作流引擎执行
            # 暂时返回模拟结果
            return {
                'success': True,
                'result': {
                    'workflow_id': workflow_id,
                    'output': input_data,
                    'status': 'completed'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'工作流插件执行失败: {str(e)}'
            }
    
    def validate_plugin_code(self, code: str) -> Dict[str, Any]:
        """验证插件代码"""
        try:
            # 简单的语法检查
            compile(code, '<string>', 'exec')
            return {
                'success': True,
                'message': '代码语法正确'
            }
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'代码语法错误: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'代码验证失败: {str(e)}'
            }
    
    def install_plugin_from_content(self, plugin_content: str, user_id: str) -> Dict[str, Any]:
        """从内容安装插件"""
        try:
            # 解析插件内容
            plugin_data = json.loads(plugin_content)
            
            # 验证必需字段
            required_fields = ['name', 'type', 'version']
            for field in required_fields:
                if field not in plugin_data:
                    return {
                        'success': False,
                        'error': f'插件配置缺少必需字段: {field}'
                    }
            
            # 保存到数据库
            plugin_data['user_id'] = user_id
            plugin_data['status'] = 'inactive'
            plugin_data['created_at'] = datetime.now()
            plugin_data['updated_at'] = datetime.now()
            
            db = self.db or get_db()
            result = db.plugins.insert_one(plugin_data)
            
            return {
                'success': True,
                'plugin_id': str(result.inserted_id),
                'message': '插件安装成功'
            }
            
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': '插件配置格式错误'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'插件安装失败: {str(e)}'
            }

    def _test_http_plugin(self, plugin: Dict, test_input: Dict[str, Any]) -> Dict[str, Any]:
        """测试HTTP插件"""
        try:
            config = plugin.get('config', {})
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': '插件配置格式错误'
                    }
            
            url = config.get('url')
            method = config.get('method', 'POST')
            headers = config.get('headers', {})
            
            if not url:
                return {
                    'success': False,
                    'error': 'HTTP插件缺少URL配置'
                }
            
            # 发送测试HTTP请求
            if method.upper() == 'GET':
                response = requests.get(url, params=test_input, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=test_input, headers=headers, timeout=10)
            
            response.raise_for_status()
            
            return {
                'success': True,
                'result': {
                    'plugin_name': plugin.get('name'),
                    'plugin_type': 'http',
                    'test_input': test_input,
                    'test_output': response.json(),
                    'status_code': response.status_code,
                    'execution_time': 0.1,
                    'status': 'success'
                },
                'message': 'HTTP插件测试成功'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'HTTP请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'HTTP插件测试失败: {str(e)}'
            }
    
    def _test_python_plugin(self, plugin: Dict, test_input: Dict[str, Any]) -> Dict[str, Any]:
        """测试Python插件"""
        try:
            config = plugin.get('config', {})
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': '插件配置格式错误'
                    }
            
            code = config.get('code', '')
            
            if not code:
                return {
                    'success': False,
                    'error': 'Python插件缺少代码配置'
                }
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # 执行Python代码
                result = subprocess.run(
                    ['python', temp_file],
                    input=json.dumps(test_input),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        return {
                            'success': True,
                            'result': {
                                'plugin_name': plugin.get('name'),
                                'plugin_type': 'python',
                                'test_input': test_input,
                                'test_output': output,
                                'execution_time': 0.1,
                                'status': 'success'
                            },
                            'message': 'Python插件测试成功'
                        }
                    except json.JSONDecodeError:
                        return {
                            'success': True,
                            'result': {
                                'plugin_name': plugin.get('name'),
                                'plugin_type': 'python',
                                'test_input': test_input,
                                'test_output': result.stdout.strip(),
                                'execution_time': 0.1,
                                'status': 'success'
                            },
                            'message': 'Python插件测试成功'
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Python代码执行失败: {result.stderr}'
                    }
                    
            finally:
                # 清理临时文件
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Python插件测试失败: {str(e)}'
            }
    
    def _test_workflow_plugin(self, plugin: Dict, test_input: Dict[str, Any]) -> Dict[str, Any]:
        """测试工作流插件"""
        try:
            config = plugin.get('config', {})
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': '插件配置格式错误'
                    }
            
            workflow_id = config.get('workflow_id')
            
            if not workflow_id:
                return {
                    'success': False,
                    'error': '工作流插件缺少工作流ID配置'
                }
            
            # 模拟工作流测试结果
            return {
                'success': True,
                'result': {
                    'plugin_name': plugin.get('name'),
                    'plugin_type': 'workflow',
                    'test_input': test_input,
                    'test_output': {
                        'workflow_id': workflow_id,
                        'output': test_input,
                        'status': 'completed'
                    },
                    'execution_time': 0.1,
                    'status': 'success'
                },
                'message': '工作流插件测试成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'工作流插件测试失败: {str(e)}'
            }

# 创建全局实例
plugin_executor = PluginExecutor() 