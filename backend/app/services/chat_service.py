"""
聊天服务模块
处理聊天相关的业务逻辑
"""

import json
import time
from typing import Generator, Dict, Any
from app.services.ollama import OllamaService

class ChatService:
    def __init__(self):
        self.ollama_service = OllamaService()
    
    def generate_response_sync(self, conversation_id: str, agent: Dict[str, Any], user_message: str) -> str:
        """
        同步生成AI回复
        """
        try:
            # 构建系统提示词
            system_prompt = agent.get('config', {}).get('system_prompt', '你是一个有用的AI助手。')
            
            # 构建完整的提示词
            full_prompt = f"{system_prompt}\n\n用户: {user_message}\n助手: "
            
            # 调用Ollama服务生成回复
            response = self.ollama_service.generate_text(
                model_name=agent.get('model_name', 'llama2'),
                prompt=full_prompt,
                temperature=agent.get('config', {}).get('temperature', 0.7),
                max_tokens=agent.get('config', {}).get('max_tokens', 1000)
            )
            
            return response.strip()
            
        except Exception as e:
            return f"抱歉，我遇到了一些问题：{str(e)}"
    
    def stream_response(self, conversation_id: str, agent: Dict[str, Any], user_message: str) -> Generator[str, None, None]:
        """
        流式生成AI回复
        """
        try:
            # 构建系统提示词
            system_prompt = agent.get('config', {}).get('system_prompt', '你是一个有用的AI助手。')
            
            # 构建完整的提示词
            full_prompt = f"{system_prompt}\n\n用户: {user_message}\n助手: "
            
            # 调用Ollama服务流式生成回复
            for chunk in self.ollama_service.stream_text(
                model_name=agent.get('model_name', 'llama2'),
                prompt=full_prompt,
                temperature=agent.get('config', {}).get('temperature', 0.7),
                max_tokens=agent.get('config', {}).get('max_tokens', 1000)
            ):
                yield chunk
                
        except Exception as e:
            yield f"抱歉，我遇到了一些问题：{str(e)}"
    
    def generate_response_with_context(self, conversation_id: str, agent: Dict[str, Any], user_message: str, context_messages: list | None = None) -> str:
        """
        基于上下文生成AI回复
        """
        try:
            # 构建系统提示词
            system_prompt = agent.get('config', {}).get('system_prompt', '你是一个有用的AI助手。')
            
            # 构建对话历史
            conversation_history = ""
            if context_messages:
                for msg in context_messages[-5:]:  # 只使用最近5条消息作为上下文
                    role = "用户" if msg['type'] == 'user' else "助手"
                    conversation_history += f"{role}: {msg['content']}\n"
            
            # 构建完整的提示词
            full_prompt = f"{system_prompt}\n\n{conversation_history}用户: {user_message}\n助手: "
            
            # 调用Ollama服务生成回复
            response = self.ollama_service.generate_text(
                model_name=agent.get('model_name', 'llama2'),
                prompt=full_prompt,
                temperature=agent.get('config', {}).get('temperature', 0.7),
                max_tokens=agent.get('config', {}).get('max_tokens', 1000)
            )
            
            return response.strip()
            
        except Exception as e:
            return f"抱歉，我遇到了一些问题：{str(e)}"
    
    def stream_response_with_context(self, conversation_id: str, agent: Dict[str, Any], user_message: str, context_messages: list | None = None) -> Generator[str, None, None]:
        """
        基于上下文流式生成AI回复
        """
        try:
            # 构建系统提示词
            system_prompt = agent.get('config', {}).get('system_prompt', '你是一个有用的AI助手。')
            
            # 构建对话历史
            conversation_history = ""
            if context_messages:
                for msg in context_messages[-5:]:  # 只使用最近5条消息作为上下文
                    role = "用户" if msg['type'] == 'user' else "助手"
                    conversation_history += f"{role}: {msg['content']}\n"
            
            # 构建完整的提示词
            full_prompt = f"{system_prompt}\n\n{conversation_history}用户: {user_message}\n助手: "
            
            # 调用Ollama服务流式生成回复
            for chunk in self.ollama_service.stream_text(
                model_name=agent.get('model_name', 'llama2'),
                prompt=full_prompt,
                temperature=agent.get('config', {}).get('temperature', 0.7),
                max_tokens=agent.get('config', {}).get('max_tokens', 1000)
            ):
                yield chunk
                
        except Exception as e:
            yield f"抱歉，我遇到了一些问题：{str(e)}" 
    
    def generate_model_response_sync(self, conversation_id: str, model: Dict[str, Any], user_message: str) -> str:
        """
        同步生成模型回复
        """
        try:
            print(f"🔧 生成模型回复 - 模型: {model.get('name', '未知')}, 提供商: {model.get('provider', '未知')}")
            
            if model.get('provider') == 'ollama':
                # 从模型配置中获取参数
                parameters = model.get('parameters', {})
                temperature = parameters.get('temperature', 0.7)
                max_tokens = parameters.get('max_tokens', 1000)
                
                # 获取Ollama服务器地址
                server_url = model.get('api_base', 'http://localhost:11434')
                print(f"🔧 使用Ollama生成 - 服务器: {server_url}, 温度: {temperature}, 最大token: {max_tokens}")
                
                # 创建Ollama服务实例
                from app.services.ollama import OllamaService
                ollama_service = OllamaService(server_url)
                
                response = ollama_service.generate_text(
                    model_name=model.get('name', 'llama2'),
                    prompt=user_message,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.strip()
            else:
                return f"模型 {model.get('name', '未知')} 的回复：{user_message}"
                
        except Exception as e:
            print(f"❌ 模型回复生成失败: {str(e)}")
            return f"抱歉，模型 {model.get('name', '未知')} 遇到了一些问题：{str(e)}"
    
    def stream_model_response(self, conversation_id: str, model: Dict[str, Any], user_message: str) -> Generator[str, None, None]:
        """
        流式生成模型回复
        """
        try:
            print(f"🔧 流式生成模型回复 - 模型: {model.get('name', '未知')}, 提供商: {model.get('provider', '未知')}")
            
            if model.get('provider') == 'ollama':
                # 从模型配置中获取参数
                parameters = model.get('parameters', {})
                temperature = parameters.get('temperature', 0.7)
                max_tokens = parameters.get('max_tokens', 1000)
                
                # 获取Ollama服务器地址
                server_url = model.get('api_base', 'http://localhost:11434')
                print(f"🔧 使用Ollama流式生成 - 服务器: {server_url}, 温度: {temperature}, 最大token: {max_tokens}")
                
                # 创建Ollama服务实例
                from app.services.ollama import OllamaService
                ollama_service = OllamaService(server_url)
                
                # 构建包含思考过程的提示词
                thinking_prompt = f"""请按照以下格式回复：

<think>
在这里分析问题，考虑各种可能性
</think>

在这里给出最终的回答

用户问题：{user_message}"""
                
                for chunk in ollama_service.stream_text(
                    model_name=model.get('name', 'llama2'),
                    prompt=thinking_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    yield chunk
            else:
                yield f"模型 {model.get('name', '未知')} 的回复：{user_message}"
                
        except Exception as e:
            print(f"❌ 流式模型回复生成失败: {str(e)}")
            yield f"抱歉，模型 {model.get('name', '未知')} 遇到了一些问题：{str(e)}" 