from flask import Flask
from app.config import Config
from app.core.extensions import init_extensions
from app.core.error_handlers import register_error_handlers
from app.blueprints.main import main
from app.blueprints.auth import auth
from app.blueprints.bot import bot


def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_object is None:
        config_object = Config
    app.config.from_object(config_object)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(bot, url_prefix="/bot")
    
    return app
