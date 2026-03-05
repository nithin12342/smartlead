"""
SmartLead Configuration
=======================
Application settings and configuration management
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "SmartLead"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/smartlead"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis Cache
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600
    
    # ML Model
    model_path: str = "/models/lead_conversion_model.pkl"
    model_version: str = "1.0.0"
    enable_model_cache: bool = True
    
    # Feature Store
    feature_store_type: str = "redis"
    feature_store_host: str = "localhost"
    feature_store_port: int = 6379
    
    # MLflow
    mlflow_tracking_uri: Optional[str] = None
    mlflow_experiment_name: str = "smartlead_lead_scoring"
    
    # Resilience
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 30
    retry_max_attempts: int = 3
    retry_initial_interval: int = 1000
    retry_max_interval: int = 30000
    
    # Observability
    enable_tracing: bool = True
    tracing_sample_rate: float = 0.1
    enable_metrics: bool = True
    
    # Azure Key Vault
    key_vault_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
    
    def __init__(self, **kwargs):
        # Get DEBUG from environment, default to False
        debug_val = os.environ.get("DEBUG", "false")
        if isinstance(debug_val, str):
            kwargs.setdefault("debug", debug_val.lower() in ("true", "1", "yes"))
        super().__init__(**kwargs)


# Global settings instance
settings = Settings()
