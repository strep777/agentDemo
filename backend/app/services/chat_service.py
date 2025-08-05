# 聊天服务模块
# 提供AI回复生成功能，支持智能体和模型两种类型
# 包含同步和流式两种生成模式

import json
import time
from typing import Dict, Any, Generator
from app.services.database import get_db
from app.services.ollama import OllamaService
from app.services.activity_service import activity_service
from bson import ObjectId
from datetime import datetime

class ChatService:
    """
    聊天服务类
    负责处理AI回复生成，支持智能体和模型两种类型
    """
    
    def __init__(self):
        """初始化聊天服务"""
        self.db = get_db()
    
    def generate_response_sync(self, conversation_id: str, agent: Dict[str, Any], user_message: str) -> str:
        """
        同步生成智能体回复
        
        Args:
            conversation_id: 对话ID
            agent: 智能体配置信息
            user_message: 用户消息
            
        Returns:
            str: AI回复内容
        """
        try:
            print(f"🤖 开始生成智能体回复 - 智能体: {agent.get('name', '未知')}")
            
            # 获取对话历史
            messages = self._get_conversation_history(conversation_id)
            
            # 构建系统提示词
            system_prompt = self._build_agent_system_prompt(agent)
            
            # 构建用户消息
            user_prompt = self._build_user_prompt(user_message, messages)
            
            # 调用Ollama生成回复
            response = self._call_ollama_for_agent(agent, system_prompt, user_prompt)
            
            print(f"✅ 智能体回复生成成功，长度: {len(response)}")
            return response
            
        except Exception as e:
            print(f"❌ 生成智能体回复失败: {str(e)}")
            raise e
    
    def generate_model_response_sync(self, conversation_id: str, model: Dict[str, Any], user_message: str) -> str:
        """
        同步生成模型回复
        
        Args:
            conversation_id: 对话ID
            model: 模型配置信息
            user_message: 用户消息
            
        Returns:
            str: AI回复内容
        """
        try:
            print(f"🤖 开始生成模型回复 - 模型: {model.get('name', '未知')}")
            
            # 获取对话历史
            messages = self._get_conversation_history(conversation_id)
            
            # 构建用户消息
            user_prompt = self._build_user_prompt(user_message, messages)
            
            # 调用Ollama生成回复
            response = self._call_ollama_for_model(model, user_prompt)
            
            print(f"✅ 模型回复生成成功，长度: {len(response)}")
            return response
            
        except Exception as e:
            print(f"❌ 生成模型回复失败: {str(e)}")
            raise e
    
    def stream_response(self, conversation_id: str, agent: Dict[str, Any], user_message: str) -> Generator[str, None, None]:
        """
        流式生成智能体回复
        
        Args:
            conversation_id: 对话ID
            agent: 智能体配置信息
            user_message: 用户消息
            
        Yields:
            str: 流式回复片段
        """
        try:
            print(f"🤖 开始流式生成智能体回复 - 智能体: {agent.get('name', '未知')}")
            
            # 获取对话历史
            messages = self._get_conversation_history(conversation_id)
            
            # 构建系统提示词
            system_prompt = self._build_agent_system_prompt(agent)
            
            # 构建用户消息
            user_prompt = self._build_user_prompt(user_message, messages)
            
            # 调用Ollama流式生成回复
            for chunk in self._call_ollama_stream_for_agent(agent, system_prompt, user_prompt):
                yield chunk
                
            print(f"✅ 智能体流式回复生成完成")
            
        except Exception as e:
            print(f"❌ 流式生成智能体回复失败: {str(e)}")
            yield f"抱歉，智能体 {agent.get('name', '未知')} 暂时无法响应：{str(e)}"
    
    def stream_model_response(self, conversation_id: str, model: Dict[str, Any], user_message: str, show_thinking: bool = False) -> Generator[str, None, None]:
        """
        流式生成模型回复
        
        Args:
            conversation_id: 对话ID
            model: 模型配置信息
            user_message: 用户消息
            show_thinking: 是否显示思考过程
            
        Yields:
            str: 流式回复片段
        """
        try:
            print(f"🤖 开始流式生成模型回复 - 模型: {model.get('name', '未知')}")
            
            # 获取对话历史
            messages = self._get_conversation_history(conversation_id)
            
            # 构建用户消息
            user_prompt = self._build_user_prompt(user_message, messages)
            
            # 调用Ollama流式生成回复
            for chunk in self._call_ollama_stream_for_model(model, user_prompt, show_thinking):
                yield chunk
                
            print(f"✅ 模型流式回复生成完成")
            
        except Exception as e:
            print(f"❌ 流式生成模型回复失败: {str(e)}")
            yield f"抱歉，模型 {model.get('name', '未知')} 暂时无法响应：{str(e)}"
    
    def _get_conversation_history(self, conversation_id: str) -> list:
        """
        获取对话历史消息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            list: 消息历史列表
        """
        try:
            # 查询最近的消息历史（限制数量以避免token过多）
            messages = list(self.db.messages.find({
                'conversation_id': ObjectId(conversation_id)
            }).sort('created_at', -1).limit(10))
            
            # 按时间正序排列
            messages.reverse()
            
            print(f"📝 获取到 {len(messages)} 条历史消息")
            return messages
            
        except Exception as e:
            print(f"❌ 获取对话历史失败: {str(e)}")
            return []
    
    def _build_agent_system_prompt(self, agent: Dict[str, Any]) -> str:
        """
        构建智能体系统提示词
        
        Args:
            agent: 智能体配置信息
            
        Returns:
            str: 系统提示词
        """
        try:
            # 基础系统提示词
            system_prompt = f"""你是一个名为"{agent.get('name', 'AI助手')}"的智能体。

{agent.get('description', '我是一个有用的AI助手，可以帮助用户解决各种问题。')}

请遵循以下指导原则：
1. 始终保持友好、专业和有用的态度
2. 根据用户的问题提供准确、相关的回答
3. 如果不确定答案，请诚实说明
4. 使用清晰、易懂的语言
5. 保持对话的自然流畅

现在开始与用户对话。"""

            # 如果有自定义的系统提示词，使用自定义的
            if agent.get('system_prompt'):
                system_prompt = agent['system_prompt']
            
            print(f"🔧 构建智能体系统提示词: {agent.get('name', '未知')}")
            return system_prompt
            
        except Exception as e:
            print(f"❌ 构建智能体系统提示词失败: {str(e)}")
            return "你是一个有用的AI助手。"
    
    def _build_user_prompt(self, user_message: str, messages: list) -> str:
        """
        构建用户消息提示词
        
        Args:
            user_message: 当前用户消息
            messages: 历史消息列表
            
        Returns:
            str: 完整的用户提示词
        """
        try:
            # 构建对话历史
            conversation_history = ""
            for msg in messages:
                if msg['type'] == 'user':
                    conversation_history += f"用户: {msg['content']}\n"
                elif msg['type'] == 'assistant':
                    conversation_history += f"助手: {msg['content']}\n"
            
            # 添加当前用户消息
            full_prompt = f"{conversation_history}用户: {user_message}\n助手:"
            
            print(f"📝 构建用户提示词，历史消息数: {len(messages)}")
            return full_prompt
            
        except Exception as e:
            print(f"❌ 构建用户提示词失败: {str(e)}")
            return f"用户: {user_message}\n助手:"
    
    def _call_ollama_for_agent(self, agent: Dict[str, Any], system_prompt: str, user_prompt: str) -> str:
        """
        调用Ollama生成智能体回复
        
        Args:
            agent: 智能体配置信息
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            str: AI回复内容
        """
        try:
            # 获取Ollama服务器地址
            server_url = agent.get('server_url', 'http://localhost:11434')
            print(f"🔧 调用Ollama生成智能体回复 - 服务器: {server_url}")
            
            # 创建Ollama服务实例
            ollama_service = OllamaService(server_url)
            
            # 获取模型名称
            model_name = agent.get('model_name', 'llama2')
            
            # 获取参数配置
            parameters = agent.get('parameters', {})
            temperature = parameters.get('temperature', 0.7)
            max_tokens = parameters.get('max_tokens', 1000)
            
            # 构建完整的提示词（包含系统提示词）
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # 调用Ollama生成回复
            response = ollama_service.generate_text(
                model_name=model_name,
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            print(f"❌ 调用Ollama生成智能体回复失败: {str(e)}")
            raise e
    
    def _call_ollama_for_model(self, model: Dict[str, Any], user_prompt: str) -> str:
        """
        调用Ollama生成模型回复
        
        Args:
            model: 模型配置信息
            user_prompt: 用户提示词
            
        Returns:
            str: AI回复内容
        """
        try:
            # 获取Ollama服务器地址，优先使用模型配置的server_url
            server_url = model.get('server_url', 'http://localhost:11434')
            print(f"🔧 使用Ollama生成 - 服务器: {server_url}")
            
            # 创建Ollama服务实例，使用模型配置的服务器地址
            from app.services.ollama import OllamaService
            ollama_service = OllamaService(server_url)
            
            # 获取模型名称
            model_name = model.get('name', 'llama2')
            
            # 获取参数配置
            parameters = model.get('parameters', {})
            temperature = parameters.get('temperature', 0.7)
            max_tokens = parameters.get('max_tokens', 1000)
            
            # 调用Ollama生成回复
            response = ollama_service.generate_text(
                model_name=model_name,
                prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            print(f"❌ 调用Ollama生成模型回复失败: {str(e)}")
            raise e
    
    def _call_ollama_stream_for_agent(self, agent: Dict[str, Any], system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """
        调用Ollama流式生成智能体回复
        
        Args:
            agent: 智能体配置信息
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Yields:
            str: 流式回复片段
        """
        try:
            # 获取Ollama服务器地址
            server_url = agent.get('server_url', 'http://localhost:11434')
            print(f"🔧 调用Ollama流式生成智能体回复 - 服务器: {server_url}")
            
            # 创建Ollama服务实例
            ollama_service = OllamaService(server_url)
            
            # 获取模型名称
            model_name = agent.get('model_name', 'llama2')
            
            # 获取参数配置
            parameters = agent.get('parameters', {})
            temperature = parameters.get('temperature', 0.7)
            max_tokens = parameters.get('max_tokens', 1000)
            
            # 构建完整的提示词（包含系统提示词）
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # 调用Ollama流式生成回复
            for chunk in ollama_service.stream_text(
                model_name=model_name,
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield chunk
                
        except Exception as e:
            print(f"❌ 调用Ollama流式生成智能体回复失败: {str(e)}")
            yield f"抱歉，智能体 {agent.get('name', '未知')} 暂时无法响应：{str(e)}"
    
    def _call_ollama_stream_for_model(self, model: Dict[str, Any], user_prompt: str, show_thinking: bool = False) -> Generator[str, None, None]:
        """
        调用Ollama流式生成模型回复
        
        Args:
            model: 模型配置信息
            user_prompt: 用户提示词
            show_thinking: 是否显示思考过程
            
        Yields:
            str: 流式回复片段
        """
        try:
            # 获取Ollama服务器地址，优先使用模型配置的server_url
            server_url = model.get('server_url', 'http://localhost:11434')
            print(f"🔧 使用Ollama流式生成 - 服务器: {server_url}")
            
            # 创建Ollama服务实例，使用模型配置的服务器地址
            from app.services.ollama import OllamaService
            ollama_service = OllamaService(server_url)
            
            # 获取模型名称
            model_name = model.get('name', 'llama2')
            
            # 获取参数配置
            parameters = model.get('parameters', {})
            temperature = parameters.get('temperature', 0.7)
            max_tokens = parameters.get('max_tokens', 1000)
            
            # 调用Ollama流式生成回复
            for chunk in ollama_service.stream_text(
                model_name=model_name,
                prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield chunk
                
        except Exception as e:
            print(f"❌ 调用Ollama流式生成模型回复失败: {str(e)}")
            yield f"抱歉，模型 {model.get('name', '未知')} 暂时无法响应：{str(e)}" 