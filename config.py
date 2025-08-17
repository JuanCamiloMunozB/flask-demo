import os

class Config:
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://myuser:mypass@localhost:5432/mydb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False
