from flask import Flask
from .bot import bot
from .auth import auth
from .extensions import db, migrate, login_manager, bcrypt
from .models import User
from flask import redirect, url_for
from flask_login import current_user


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configuración de Login
    login_manager.login_view = 'auth.login'

    # Registro con o sin prefijo
    app.register_blueprint(bot, url_prefix="/bot")
    app.register_blueprint(auth, url_prefix="/auth")

    # Ruta raíz: redirige al login si el usuario no está autenticado, o al chat (/bot/) si lo está
    @app.route('/')
    def root():
        if current_user.is_authenticated:
            return redirect(url_for('bot.index'))
        return redirect(url_for('auth.login'))

    # user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
