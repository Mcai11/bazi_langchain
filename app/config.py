import os
from typing import Optional, Dict, Any
from enum import Enum

# Database configuration for Postgres + pgvector
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "LangChainDB"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "19951217"  # Change to your actual password

class LLMProvider(Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    BAICHUAN = "baichuan"

class Settings:
    # LLM配置
    LLM_PROVIDER: str = "deepseek"  # 默认使用DeepSeek
    
    # API密钥配置
    API_KEYS: Dict[str, str] = {
        "deepseek": "sk-d8d0ad8fda5a4f8dbbc8cbd95204d2c1",
        "openai": "",  # 需要时填入
        "claude": "",  # 需要时填入
        "qwen": "",    # 需要时填入
        "baichuan": "", # 需要时填入
    }
    
    # 模型配置
    MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
        "deepseek": {
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "openai": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "claude": {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "qwen": {
            "model": "qwen-plus",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "baichuan": {
            "model": "baichuan2-13b-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    }
    
    def __init__(self):
        # 优先使用环境变量
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.LLM_PROVIDER)
        
        # 从环境变量更新API密钥
        for provider in self.API_KEYS:
            env_key = f"{provider.upper()}_API_KEY"
            env_value = os.getenv(env_key)
            if env_value:
                self.API_KEYS[provider] = env_value
    
    def get_current_api_key(self) -> str:
        """获取当前LLM提供商的API密钥"""
        return self.API_KEYS.get(self.LLM_PROVIDER, "")
    
    def get_current_model_config(self) -> Dict[str, Any]:
        """获取当前LLM的模型配置"""
        return self.MODEL_CONFIGS.get(self.LLM_PROVIDER, {})
    
    def get_supported_providers(self) -> list:
        """获取支持的LLM提供商列表"""
        return list(self.API_KEYS.keys())
    
    def is_provider_configured(self, provider: Optional[str] = None) -> bool:
        """检查指定提供商是否配置了API密钥"""
        if provider is None:
            provider = self.LLM_PROVIDER
        return bool(self.API_KEYS.get(provider, "").strip())

settings = Settings() 