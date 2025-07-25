from typing import Any
from pydantic import SecretStr
from app.config import settings

def create_llm():
    """根据配置创建对应的LLM实例"""
    provider = settings.LLM_PROVIDER
    api_key = settings.get_current_api_key()
    model_config = settings.get_current_model_config()
    
    if not api_key:
        raise ValueError(f"API key for {provider} is not configured. Please set {provider.upper()}_API_KEY environment variable or update config.py")
    
    api_key_secret = SecretStr(api_key)
    
    try:
        if provider == "deepseek":
            from langchain_deepseek import ChatDeepSeek
            return ChatDeepSeek(
                model=model_config.get("model", "deepseek-chat"),
                api_key=api_key_secret,
                temperature=model_config.get("temperature", 0.7)
            )
        
        elif provider == "openai":
            from langchain_openai import ChatOpenAI  # type: ignore
            return ChatOpenAI(
                model=model_config.get("model", "gpt-4"),
                api_key=api_key_secret,
                temperature=model_config.get("temperature", 0.7)
            )
        
        elif provider == "claude":
            from langchain_anthropic import ChatAnthropic  # type: ignore
            return ChatAnthropic(
                model=model_config.get("model", "claude-3-sonnet-20240229"),
                api_key=api_key_secret,
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 2000)
            )
        
        elif provider == "qwen":
            # 注意：这里需要安装对应的langchain包
            try:
                from langchain_community.llms import QianfanLLMEndpoint  # type: ignore
                return QianfanLLMEndpoint(
                    model=model_config.get("model", "qwen-plus"),
                    qianfan_ak=api_key,
                    temperature=model_config.get("temperature", 0.7),
                    top_p=0.8,
                )
            except ImportError:
                raise ImportError("Please install langchain-community to use Qwen models")
        
        elif provider == "baichuan":
            # 注意：这里需要安装对应的langchain包
            try:
                from langchain_community.llms import BaichuanLLM  # type: ignore
                return BaichuanLLM(
                    baichuan_api_key=api_key,
                    model_name=model_config.get("model", "baichuan2-13b-chat"),
                    temperature=model_config.get("temperature", 0.7),
                )
            except ImportError:
                raise ImportError("Please install langchain-community to use Baichuan models")
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: {settings.get_supported_providers()}")
    
    except ImportError as e:
        raise ImportError(f"Failed to import {provider} LLM library. Error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {provider} LLM. Error: {str(e)}")

def get_provider_info():
    """获取当前提供商信息"""
    provider = settings.LLM_PROVIDER
    model_config = settings.get_current_model_config()
    is_configured = settings.is_provider_configured()
    
    return {
        "provider": provider,
        "model": model_config.get("model", "unknown"),
        "is_configured": is_configured,
        "supported_providers": settings.get_supported_providers()
    }

def test_llm_connection():
    """测试LLM连接"""
    try:
        llm = create_llm()
        # 简单测试
        test_prompt = "Hello, please respond with 'Connection successful'"
        response = llm.invoke(test_prompt)
        return {
            "success": True,
            "provider": settings.LLM_PROVIDER,
            "response": response.content if hasattr(response, 'content') else str(response)
        }
    except Exception as e:
        return {
            "success": False,
            "provider": settings.LLM_PROVIDER,
            "error": str(e)
        } 