import requests
import json
import os
from typing import List, Dict, Any, Optional, Union, Generator
from app.services.database import get_db
from app.models.model import Model
from bson import ObjectId

# 主进程标志 - 通过环境变量判断
_is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if _is_main_process:
            print(f"🔧 OllamaService初始化: {self.base_url}")
            # 启动时不检测连接，只在需要时才检测
    
    def _get_model_config(self, model_name: str) -> Optional[Dict]:
        """获取模型配置"""
        try:
            db = get_db()
            model = db.models.find_one({'name': model_name})
            if model:
                return {
                    'api_base': model.get('server_url', self.base_url),
                    'api_key': model.get('api_key', ''),
                    'max_tokens': model.get('max_tokens', 4096),
                    'temperature': model.get('temperature', 0.7),
                    'top_p': model.get('top_p', 1.0),
                    'frequency_penalty': model.get('frequency_penalty', 0.0),
                    'presence_penalty': model.get('presence_penalty', 0.0)
                }
        except Exception as e:
            if _is_main_process:
                print(f"获取模型配置失败: {str(e)}")
        
        # 返回默认配置
        return {
            'api_base': self.base_url,
            'api_key': '',
            'max_tokens': 4096,
            'temperature': 0.7,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 只在主进程中打印健康检查信息
            if _is_main_process:
                print(f"🏥 检查Ollama健康状态: {self.base_url}/api/tags")
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if _is_main_process:
                print(f"📊 响应状态码: {response.status_code}")
            if response.status_code == 200:
                if _is_main_process:
                    print("✅ Ollama服务器连接正常")
                return True
            else:
                if _is_main_process:
                    print(f"❌ Ollama服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            if _is_main_process:
                print(f"❌ Ollama服务器连接失败: {str(e)}")
            return False
        except requests.exceptions.Timeout as e:
            if _is_main_process:
                print(f"❌ Ollama服务器连接超时: {str(e)}")
            return False
        except Exception as e:
            if _is_main_process:
                print(f"❌ Ollama健康检查异常: {str(e)}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        try:
            # 只在主进程中打印模型列表获取信息
            if _is_main_process:
                print(f"📋 获取Ollama模型列表: {self.base_url}/api/tags")
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            
            if _is_main_process:
                print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                if _is_main_process:
                    print(f"❌ 获取模型列表失败: {response.status_code} - {response.text}")
                raise Exception(f"获取模型列表失败: {response.status_code} - {response.text}")
            
            result = response.json()
            models = result.get('models', [])
            if _is_main_process:
                print(f"✅ 发现 {len(models)} 个模型")
            return models
            
        except requests.exceptions.ConnectionError as e:
            if _is_main_process:
                print(f"❌ Ollama服务器连接失败: {str(e)}")
            raise Exception(f"Ollama服务器连接失败: {str(e)}")
        except requests.exceptions.Timeout as e:
            if _is_main_process:
                print(f"❌ Ollama服务器连接超时: {str(e)}")
            raise Exception(f"Ollama服务器连接超时: {str(e)}")
        except Exception as e:
            if _is_main_process:
                print(f"❌ 获取模型列表失败: {str(e)}")
            raise Exception(f"获取模型列表失败: {str(e)}")
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """拉取模型"""
        try:
            # 只在主进程中打印拉取模型信息
            if _is_main_process:
                print(f"📥 拉取模型: {model_name}")
            payload = {'name': model_name}
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=300  # 拉取模型可能需要较长时间
            )
            
            if _is_main_process:
                print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                if _is_main_process:
                    print(f"❌ 拉取模型失败: {response.status_code} - {response.text}")
                raise Exception(f"拉取模型失败: {response.status_code} - {response.text}")
            
            result = response.json()
            if _is_main_process:
                print("✅ 模型拉取成功")
            return result
            
        except Exception as e:
            if _is_main_process:
                print(f"❌ 拉取模型失败: {str(e)}")
            raise Exception(f"拉取模型失败: {str(e)}")
    
    def chat(self, model: str, messages: List[Dict[str, str]], 
             temperature: float = 0.7, max_tokens: int = 2000,
             stream: bool = False) -> Union[Dict[str, Any], requests.Response]:
        """
        与Ollama模型进行对话
        
        Args:
            model: 模型名称
            messages: 消息列表，格式为 [{'role': 'user', 'content': '...'}]
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式返回
            
        Returns:
            包含回复的字典
        """
        try:
            print(f"💬 开始聊天: 模型={model}, 温度={temperature}, 最大token={max_tokens}")
            
            # 获取模型配置
            config = self._get_model_config(model)
            if config is None:
                config = {
                    'api_base': self.base_url,
                    'api_key': '',
                    'max_tokens': 4096,
                    'temperature': 0.7,
                    'top_p': 1.0,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                }
            
            # 构建请求数据
            payload = {
                'model': model,
                'messages': messages,
                'stream': stream,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': config.get('top_p', 1.0),
                    'frequency_penalty': config.get('frequency_penalty', 0.0),
                    'presence_penalty': config.get('presence_penalty', 0.0)
                }
            }
            
            if _is_main_process:
                print(f"📤 发送请求到: {config['api_base']}/api/chat")
            
            # 发送请求
            response = self.session.post(
                f"{config['api_base']}/api/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if _is_main_process:
                print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                if _is_main_process:
                    print(f"❌ Ollama API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API请求失败: {response.status_code} - {response.text}")
            
            if stream:
                return response
            else:
                result = response.json()
                if _is_main_process:
                    print("✅ 聊天完成")
                return {
                    'content': result.get('message', {}).get('content', ''),
                    'model': result.get('model', model),
                    'usage': result.get('usage', {}),
                    'done': result.get('done', True)
                }
                
        except Exception as e:
            if _is_main_process:
                print(f"❌ Ollama服务调用失败: {str(e)}")
            raise Exception(f"Ollama服务调用失败: {str(e)}")
    
    def generate(self, model: str, prompt: str, 
                temperature: float = 0.7, max_tokens: int = 2000,
                stream: bool = False) -> Union[Dict[str, Any], requests.Response]:
        """
        使用Ollama模型生成文本
        
        Args:
            model: 模型名称
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式返回
            
        Returns:
            包含生成文本的字典
        """
        try:
            print(f"📝 开始生成: 模型={model}, 提示词长度={len(prompt)}")
            
            # 获取模型配置
            config = self._get_model_config(model)
            if config is None:
                config = {
                    'api_base': self.base_url,
                    'api_key': '',
                    'max_tokens': 4096,
                    'temperature': 0.7,
                    'top_p': 1.0,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                }
            
            # 构建请求数据
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': stream,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': config.get('top_p', 1.0),
                    'frequency_penalty': config.get('frequency_penalty', 0.0),
                    'presence_penalty': config.get('presence_penalty', 0.0)
                }
            }
            
            if _is_main_process:
                print(f"📤 发送请求到: {config['api_base']}/api/generate")
            
            # 发送请求
            response = self.session.post(
                f"{config['api_base']}/api/generate",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if _is_main_process:
                print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                if _is_main_process:
                    print(f"❌ Ollama API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API请求失败: {response.status_code} - {response.text}")
            
            if stream:
                return response
            else:
                result = response.json()
                if _is_main_process:
                    print("✅ 文本生成完成")
                return {
                    'content': result.get('response', ''),
                    'model': result.get('model', model),
                    'usage': result.get('usage', {}),
                    'done': result.get('done', True)
                }
                
        except Exception as e:
            if _is_main_process:
                print(f"❌ Ollama服务调用失败: {str(e)}")
            raise Exception(f"Ollama服务调用失败: {str(e)}") 

    def generate_text(self, model_name: str, prompt: str, 
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        生成文本（简化版本）
        """
        try:
            # 直接尝试生成，不进行健康检查
            result = self.generate(model_name, prompt, temperature, max_tokens, stream=False)
            # 处理返回的字典类型
            if isinstance(result, dict):
                return result.get('content', '抱歉，生成失败')
            else:
                return '抱歉，生成失败'
        except Exception as e:
            print(f"❌ 文本生成失败: {str(e)}")
            raise e
    
    def stream_text(self, model_name: str, prompt: str, 
                   temperature: float = 0.7, max_tokens: int = 1000) -> Generator[str, None, None]:
        """
        流式生成文本
        """
        try:
            print(f"📝 开始生成: 模型={model_name}, 提示词长度={len(prompt)}")
            
            # 直接尝试生成，不进行健康检查
            response = self.generate(model_name, prompt, temperature, max_tokens, stream=True)
            
            # 处理返回的Response对象
            from requests import Response
            if isinstance(response, Response):
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                raise Exception("流式生成失败")
                            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ollama连接失败: {str(e)}")
            yield f"抱歉，无法连接到AI模型服务器。请检查网络连接或联系管理员。"
        except requests.exceptions.Timeout as e:
            print(f"❌ Ollama请求超时: {str(e)}")
            yield f"抱歉，AI模型响应超时。请稍后重试。"
        except Exception as e:
            print(f"❌ 流式文本生成失败: {str(e)}")
            yield f"抱歉，生成回复时遇到错误：{str(e)}" 