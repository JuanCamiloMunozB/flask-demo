import os
from app.config.base import Config as BaseConfig
from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig
from app.config.testing import TestingConfig

# Default configuration for backwards compatibility
Config = BaseConfig

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, Config)
    