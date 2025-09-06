from .base import Config


class DevelopmentConfig(Config):
    """Development configuration class."""
    
    DEBUG = True
    TESTING = False
