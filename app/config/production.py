from .base import Config


class ProductionConfig(Config):
    """Production configuration class."""
    
    DEBUG = False
    TESTING = False
