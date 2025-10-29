"""
Configuration settings for Compliance Master API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # IBM WatsonX Configuration
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    
    # Model Configuration
    granite_model_id: str = "ibm/granite-13b-chat-v2"
    
    # API Configuration
    api_title: str = "Compliance Master API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered document processing and ISO template generation"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

