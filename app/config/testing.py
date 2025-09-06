from .base import Config


class TestingConfig(Config):
    """Testing configuration class."""
    
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
