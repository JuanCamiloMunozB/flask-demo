# Asistente de Apuestas (Flask)

## Integrantes

- Martín Gómez
- Juan Camilo Muñoz

## ¿De qué trata?

Aplicación web en Flask que guía a la persona usuaria paso a paso para evaluar si una apuesta deportiva es segura o arriesgada. Para ello combina:

- Sistemas expertos (reglas con experta) y
- Redes bayesianas (inferencia con pgmpy) para dos deportes: fútbol (soccer) y baloncesto (basketball).
- Incluye autenticación (registro / login con Flask-Login y Flask-WTF), persistencia con SQLAlchemy y migraciones con Flask-Migrate. La estructura modular separa auth y el bot con sus modelos, assets y vistas.

## Tecnologías principales

## Tecnologías

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask)](https://flask.palletsprojects.com/)
[![Flask-Login](https://img.shields.io/badge/Flask--Login-Auth-lightgrey)](https://flask-login.readthedocs.io/)
[![Flask-WTF](https://img.shields.io/badge/Flask--WTF-Forms-green)](https://flask-wtf.readthedocs.io/)
[![WTForms](https://img.shields.io/badge/WTForms-Validation-forestgreen)](https://wtforms.readthedocs.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)](https://www.sqlalchemy.org/)
[![Flask-Migrate](https://img.shields.io/badge/Flask--Migrate-Alembic-orange)](https://flask-migrate.readthedocs.io/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange)](https://alembic.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-336791?logo=postgresql)](https://www.postgresql.org/)
[![psycopg2](https://img.shields.io/badge/psycopg2-Driver-blue)](https://www.psycopg.org/)
[![python-dotenv](https://img.shields.io/badge/python--dotenv-Env-9cf)](https://github.com/theskumar/python-dotenv)

[![Experta](https://img.shields.io/badge/Experta-Rule_Engine-lightgrey)](https://github.com/nilp0inter/experta)
[![pgmpy](https://img.shields.io/badge/pgmpy-Bayesian_Inference-orange)](https://pgmpy.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Numerics-013243?logo=numpy)](https://numpy.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas)](https://pandas.pydata.org/)

[![Jinja2](https://img.shields.io/badge/Jinja2-Templating-yellow)](https://palletsprojects.com/p/jinja/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-UI-7952B3?logo=bootstrap)](https://getbootstrap.com/)
[![Font Awesome](https://img.shields.io/badge/Font%20Awesome-Icons-528DD7?logo=fontawesome)](https://fontawesome.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=000)](https://developer.mozilla.org/docs/Web/JavaScript)

[![Flask-Bcrypt](https://img.shields.io/badge/Flask--Bcrypt-Passwords-4B8BBE)](https://flask-bcrypt.readthedocs.io/)
[![pytest](https://img.shields.io/badge/pytest-Testing-0A9EDC?logo=pytest)](https://docs.pytest.org/)


## Estructura (resumida)

```bash 
exposicion-flask/
  app/
    blueprints/
      auth/              # Blueprint de autenticación (registro/login)
        __init__.py      # Definición del blueprint
        forms.py         # Formularios Flask-WTF
        routes.py        # Rutas de autenticación
      bot/               # Blueprint del bot conversacional
      main/              # Blueprint principal
    config/              # Configuraciones por ambiente
      base.py            # Configuración base y construcción de DB URI
      development.py     # Configuración de desarrollo
      production.py      # Configuración de producción
      testing.py         # Configuración de testing
    core/                # Núcleo de la aplicación
      extensions.py      # Inicialización de extensiones (db, login_manager, etc.)
      error_handlers.py  # Manejadores de errores
      exceptions.py      # Excepciones personalizadas
    models/              # Modelos de base de datos
      user.py            # Modelo de usuario
      chat.py            # Modelos de chat (ChatSession, ChatMessage)
    services/            # Servicios de negocio
      auth_service.py    # Lógica de autenticación
      betting_service.py # Lógica de apuestas
      chat_service.py    # Lógica del chat
    ai/                  # Módulos de IA
      betting_adviser.py # Asesor principal de apuestas
      models/            # Modelos de IA (bayesianos y sistemas expertos)
    templates/           # Plantillas HTML compartidas
    static/              # Archivos estáticos compartidos
    __init__.py          # Factory de la aplicación Flask
  migrations/            # Migraciones de Alembic
  tests/                 # Tests (unit, integration, stress, validation)
  config.py              # Configuración principal y factory
  run.py                 # Punto de entrada

```

## Configuración de entorno 

El archivo `config/base.py` permite dos rutas:

1. **DATABASE_URL** (recomendada en despliegues): si está presente, se usa tal cual y fuerza sslmode=require si falta.

2. **Variables SUPABASE_*** para construir la URI:
`SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`.
Además, define `SECRET_KEY` y opciones del engine.

### Ejemplo .env 

```env
FLASK_ENV=development
SECRET_KEY=change-me
# Opción 1: URL directa
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db?sslmode=require
# Opción 2: piezas SUPABASE_*
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=flask_demo
```

### Instalación y ejecución local

### 1. Clonar e ir al proyecto

```bash
git clone https://github.com/JuanCamiloMunozB/flask-demo.git
cd flask-demo
````

### 2. Crear y activar entorno

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
python -m pip install -U pip
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
pip install --upgrade frozendict
```
### 4. Configurar variables 
Crear el .env como arriba. 

### 5. Inicializar la base de datos
```bash
# Crear tablas con migraciones existentes
flask db upgrade
```
### 6. Levantar la app

```bash
flask run
```

## Despliegue

La aplicación desplegada la puedes encontrar [aquí](https://flask-demo-t2t8.onrender.com)



# Instrucciones para crear el apartado de login con las tecnologías de Flask

Objetivo: levantar un mini-proyecto con registro, login, logout usando Flask, Flask-Login, Flask-WTF, SQLAlchemy, Flask-Migrate y PostgreSQL de Supabase. Esta guía sigue la estructura modular utilizada en el proyecto principal con blueprints separados, servicios de negocio y configuración por ambientes.

## 1) Crear proyecto y entorno

```bash
mkdir flask-login-demo 
cd flask-login-demo
python -m venv .venv
# Windows: 
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
python -m pip install -U pip
pip install flask flask_sqlalchemy flask_migrate flask_login flask_wtf flask_bcrypt python-dotenv psycopg2-binary

```

## 2) Obtener credenciales de Supabase (Postgres)
- Crea un proyecto en Supabase.
- En el panel del proyecto: Database → Connect
- Copia host, port, database, user, password o la connection string
- Recomendamos usar el Transaction pooler para garantizar compatibilidad con IPv4 

![alt text](images/image1.png)


Usaremos variables SUPABASE_DB_* o DATABASE_URL (cualquiera de las dos).

## 3) Estructura modular

```bash
flask-login-demo/
  app/
    blueprints/
      auth/
        __init__.py               # Blueprint 'auth'
        forms.py                  # Flask-WTF forms
        routes.py                 # Rutas /register, /login, /logout
    config/
      __init__.py
      base.py                     # Configuración base y construcción de DB URI
    core/
      __init__.py
      extensions.py               # db, migrate, login_manager, bcrypt
    models/
      __init__.py
      user.py                     # Modelo User
    services/
      __init__.py
      auth_service.py             # Lógica de autenticación
    templates/
      auth/
        login.html              
        register.html
    static/
      css/
        style.css      
    __init__.py                   # create_app factory
  migrations/                     # Se creará al correr 'flask db init'
  config.py                       # Configuración principal
  .env                            # Credenciales
  run.py                          # Entry point

```

## 4) Archivos para copiar/pegar

### 4.1 .env

```env
FLASK_ENV=development
SECRET_KEY=change-me

# Opción 1: cadena completa
# DATABASE_URL=postgresql://postgres.mzolmdqoxbjndfgwihcu:[YOUR-PASSWORD]@aws-1-us-east-2.pooler.supabase.com:6543/postgressslmode=require
# Opción 2: piezas Supabase
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
SUPABASE_DB_HOST=db.xxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
```
Recuerda cambiar las variables a las que obtengas de supabase

### 4.2 config.py

```python
# config.py
import os
from app.config.base import Config

# Factory de configuración que retorna la clase de configuración apropiada
# según la variable de entorno FLASK_ENV
def get_config():
    # Obtiene el entorno actual (development por defecto)
    env = os.getenv('FLASK_ENV', 'development')
    
    # Importa y retorna la configuración específica del entorno
    if env == 'production':
        from app.config.production import ProductionConfig
        return ProductionConfig
    elif env == 'testing':
        from app.config.testing import TestingConfig
        return TestingConfig
    else:
        # Por defecto usa configuración de desarrollo
        from app.config.development import DevelopmentConfig
        return DevelopmentConfig
```

### 4.3 app/config/base.py

```python
# app/config/base.py
import os
from urllib.parse import quote_plus

def build_db_uri():
    """Build database URI from environment variables."""
    # Opción 1: Usar DATABASE_URL directa (preferida en despliegues como Heroku)
    url = os.getenv("DATABASE_URL")
    if url:
        # Si existe DATABASE_URL, verificar que tenga sslmode=require para seguridad
        return url if "sslmode=" in url else (url + ("&" if "?" in url else "?") + "sslmode=require")
    
    # Opción 2: Construir URI desde variables individuales de Supabase
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    pwd = quote_plus(os.getenv("SUPABASE_DB_PASSWORD", ""))  # quote_plus codifica caracteres especiales
    host = os.getenv("SUPABASE_DB_HOST", "localhost")
    port = os.getenv("SUPABASE_DB_PORT", "5432")
    name = os.getenv("SUPABASE_DB_NAME", "postgres")
    
    # Construye la URI completa con SSL obligatorio
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}?sslmode=require"

class Config:
    """Base configuration class."""
    # Clave secreta para firmar cookies y tokens CSRF
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    
    # URI de conexión a la base de datos
    SQLALCHEMY_DATABASE_URI = build_db_uri()
    
    # Desactiva el tracking de modificaciones (ahorra memoria)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuraciones del engine de SQLAlchemy para optimizar conexiones
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,        # Verifica conexiones antes de usarlas
        "pool_recycle": 300,          # Recicla conexiones cada 5 minutos
        "connect_args": {"sslmode": "require"},  # Fuerza SSL en todas las conexiones
    }
```

### 4.4 app/config/development.py

```python
# app/config/development.py
from .base import Config

class DevelopmentConfig(Config):
    """Development configuration."""
    # Activa el modo debug para recarga automática y mejor debugging
    DEBUG = True
```

### 4.5 app/core/extensions.py

```python
# app/core/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Inicialización de extensiones sin app (patrón de fábrica)
db = SQLAlchemy()           # ORM para manejo de base de datos
migrate = Migrate()         # Sistema de migraciones de esquema
login_manager = LoginManager()  # Manejo de sesiones de usuario
bcrypt = Bcrypt()          # Hash seguro de contraseñas

def init_extensions(app):
    """Initialize Flask extensions with the app instance."""
    # Vincula todas las extensiones con la instancia de Flask
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configuración específica del login manager
    login_manager.login_view = 'auth.login'  # Ruta por defecto para login
    
    # Función para cargar usuarios desde la base de datos
    @login_manager.user_loader
    def load_user(user_id):
        # Importación circular evitada importando aquí
        from app.models.user import User
        return User.query.get(int(user_id))
```

### 4.6 app/models/user.py

```python
# app/models/user.py
from flask_login import UserMixin
from app.core.extensions import db, bcrypt

class User(UserMixin, db.Model):
    """User model for authentication."""
    # Nombre específico de tabla para evitar conflictos con 'users' reservado
    __tablename__ = 'app_users'
    
    # Campos de la tabla
    id = db.Column(db.Integer, primary_key=True)  # ID único autoincremental
    username = db.Column(db.String(80), unique=True, nullable=False)  # Nombre único de usuario
    password_hash = db.Column(db.String(128), nullable=False)  # Hash de la contraseña (nunca texto plano)

    def set_password(self, password: str):
        """Set the user's password hash."""
        # Genera hash seguro de la contraseña usando bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password hash."""
        # Verifica si la contraseña coincide con el hash almacenado
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        """String representation of the user object."""
        return f"<User {self.username}>"
```

### 4.7 app/services/auth_service.py

```python
# app/services/auth_service.py
from app.models.user import User
from app.core.extensions import db
from app.core.exceptions import AuthenticationError

class AuthService:
    """Service for user authentication operations."""
    
    @staticmethod
    def register_user(username: str, password: str) -> User:
        """Register a new user."""
        # Verifica si el usuario ya existe en la base de datos
        if User.query.filter_by(username=username).first():
            raise AuthenticationError("Username already exists")
        
        # Crea un nuevo usuario con contraseña hasheada
        user = User(username=username)
        user.set_password(password)  # Método que genera el hash seguro
        
        # Guarda el usuario en la base de datos
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """Authenticate a user with username and password."""
        # Busca el usuario por nombre de usuario
        user = User.query.filter_by(username=username).first()
        
        # Verifica que existe y que la contraseña es correcta
        if user and user.check_password(password):
            return user
        
        # Si no existe o contraseña incorrecta, lanza excepción
        raise AuthenticationError("Invalid credentials")
```

### 4.8 app/core/exceptions.py

```python
# app/core/exceptions.py
class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    # Excepción personalizada para errores de autenticación
    # Permite mejor manejo de errores específicos del dominio
    pass
```

### 4.9 app/__init__.py (App factory)

```python
# app/__init__.py
from flask import Flask, redirect, url_for
from flask_login import current_user
from app.core.extensions import init_extensions
from app.blueprints.auth import auth

def create_app(config_object=None):
    """Create and configure the Flask application."""
    # Crea la instancia principal de Flask
    app = Flask(__name__)
    
    # Carga la configuración apropiada según el entorno
    if config_object is None:
        from config import get_config
        config_object = get_config()
    app.config.from_object(config_object)
    
    # Inicializa todas las extensiones (db, login_manager, etc.)
    init_extensions(app)
    
    # Registra los blueprints (módulos de rutas)
    app.register_blueprint(auth, url_prefix="/auth")
    
    # Ruta raíz que redirige según el estado de autenticación
    @app.route('/')
    def root():
        # Si el usuario está autenticado, muestra mensaje de bienvenida
        if current_user.is_authenticated:
            return f"<h1>Bienvenido {current_user.username}!</h1><a href='/auth/logout'>Cerrar sesión</a>"
        # Si no está autenticado, redirige al login
        return redirect(url_for('auth.login'))
    
    return app
```

### 4.10 app/blueprints/auth/__init__.py

```python
# app/blueprints/auth/__init__.py
from flask import Blueprint

# Crea el blueprint de autenticación
auth = Blueprint(
    "auth", __name__,
    # Especifica dónde encontrar templates y archivos estáticos
    template_folder="../../templates/auth",  # Ruta relativa a templates
    static_folder="../../static"             # Ruta relativa a archivos estáticos
)

# Importa las rutas después de crear el blueprint para evitar importaciones circulares
from . import routes
```

### 4.11 app/blueprints/auth/forms.py

```python
# app/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models.user import User

class RegisterForm(FlaskForm):
    """User registration form."""
    # Campo de nombre de usuario con validaciones
    username = StringField('Username', validators=[
        DataRequired(),        # Campo obligatorio
        Length(3, 80)         # Entre 3 y 80 caracteres
    ])
    
    # Campo de contraseña con validaciones
    password = PasswordField('Password', validators=[
        DataRequired(),        # Campo obligatorio
        Length(6, 128)        # Entre 6 y 128 caracteres
    ])
    
    # Campo de confirmación de contraseña
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),        # Campo obligatorio
        EqualTo('password')   # Debe ser igual al campo 'password'
    ])
    
    # Botón de envío
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate that username is unique."""
        # Validación personalizada: verifica que el username no exista
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already in use')

class LoginForm(FlaskForm):
    """User login form."""
    # Campos básicos para login
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```

### 4.12 app/blueprints/auth/routes.py

```python
# app/blueprints/auth/routes.py
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from .forms import RegisterForm, LoginForm
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = RegisterForm()
    
    if request.method == 'POST':
        # Si el formulario es válido (pasa todas las validaciones)
        if form.validate_on_submit():
            try:
                # Intenta registrar el usuario usando el servicio
                user = AuthService.register_user(form.username.data, form.password.data)
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except AuthenticationError as e:
                # Si hay error (ej: usuario ya existe), muestra mensaje
                flash(str(e), 'error')
        # Si hay errores de validación, re-renderiza con errores
        return render_template('register.html', form=form), 400
    
    # GET request: muestra formulario vacío
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    
    if request.method == 'POST':
        # Si el formulario es válido
        if form.validate_on_submit():
            try:
                # Intenta autenticar al usuario
                user = AuthService.authenticate_user(form.username.data, form.password.data)
                login_user(user)  # Inicia la sesión del usuario
                flash('Login successful!', 'success')
                return redirect(url_for('root'))  # Redirige a página principal
            except AuthenticationError as e:
                # Credenciales inválidas
                flash(str(e), 'error')
        # Errores de validación o autenticación
        return render_template('login.html', form=form), 400
    
    # GET request: muestra formulario de login
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required  # Decorador que requiere que el usuario esté autenticado
def logout():
    """Logout the current user."""
    logout_user()  # Termina la sesión del usuario
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

### 4.13 app/templates/auth/register.html

```html
<!-- app/templates/auth/register.html -->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Registro - Asistente de Apuestas</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('auth.static', filename='css/common.css') }}" />
</head>
<body>

<div class="chat-container d-flex flex-column">
  <div class="chat-header">
    <div class="title">
      <i class="fas fa-dice fa-lg me-2 icon-custom"></i>
      <strong>Registro</strong>
    </div>
  </div>

  <div class="chat-body p-4">
    <form method="post" action="{{ url_for('auth.register') }}" novalidate>
      {{ form.hidden_tag() }}

      <!--
      Este bloque de código utiliza la función `get_flashed_messages` de Flask para mostrar mensajes flash en la interfaz. Primero, obtiene los mensajes junto con sus categorías. Si existen mensajes, los recorre y muestra cada uno en un div con una clase de alerta de Bootstrap: si la categoría es 'error', se muestra como 'danger', de lo contrario como 'success'. Esto permite informar al usuario sobre el resultado de acciones recientes, como errores o confirmaciones.
      -->
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
              {{ message }}
            </div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      {% if form.errors %}
      <div class="alert alert-danger">
        <ul class="mb-0">
          {% for field, errors in form.errors.items() %}
            {% for err in errors %}
              <li>{{ err }}</li>
            {% endfor %}
          {% endfor %}
        </ul>
      </div>
      {% endif %}

      <div class="mb-3">
        {{ form.username.label(class_='form-label') }}
        {{ form.username(class_='form-control input-dark', placeholder='Usuario') }}
      </div>

      <div class="mb-3">
        {{ form.password.label(class_='form-label') }}
        {{ form.password(class_='form-control input-dark', placeholder='Contraseña') }}
      </div>

      <div class="mb-3">
        {{ form.confirm.label(class_='form-label') }}
        {{ form.confirm(class_='form-control input-dark', placeholder='Confirma la contraseña') }}
      </div>

      <div class="d-grid gap-2">
        {{ form.submit(class_='btn send-btn') }}
      </div>
    </form>

    <div class="text-center mt-3">
      <a href="{{ url_for('auth.login') }}" class="text-accent">¿Ya tienes cuenta? Inicia sesión</a>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 4.14 app/templates/auth/login.html

```html
<!-- app/templates/auth/login.html -->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Login - Asistente de Apuestas</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('auth.static', filename='css/common.css') }}" />
</head>
<body>

<div class="chat-container d-flex flex-column">
  <div class="chat-header">
    <div class="title">
      <i class="fas fa-dice fa-lg me-2 icon-custom"></i>
      <strong>Iniciar sesión</strong>
    </div>
  </div>

  <div class="chat-body p-4">
    <form method="post" action="{{ url_for('auth.login') }}" novalidate>
      {{ form.hidden_tag() }}

      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
              {{ message }}
            </div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      {% if form.errors %}
      <div class="alert alert-danger">
        <ul class="mb-0">
          {% for field, errors in form.errors.items() %}
            {% for err in errors %}
              <li>{{ err }}</li>
            {% endfor %}
          {% endfor %}
        </ul>
      </div>
      {% endif %}

      <div class="mb-3">
        {{ form.username.label(class_='form-label') }}
        {{ form.username(class_='form-control input-dark', placeholder='Usuario') }}
      </div>

      <div class="mb-3">
        {{ form.password.label(class_='form-label') }}
        {{ form.password(class_='form-control input-dark', placeholder='Contraseña') }}
      </div>

      <div class="d-grid gap-2">
        {{ form.submit(class_='btn send-btn') }}
      </div>
    </form>

    <div class="text-center mt-3">
      <a href="{{ url_for('auth.register') }}" class="text-accent">¿No tienes cuenta? Regístrate</a>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 4.15 run.py

```python
# run.py
import os
from app import create_app
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Crea la aplicación Flask usando el factory pattern
app = create_app()

if __name__ == '__main__':
    # Ejecuta la aplicación solo si este archivo se ejecuta directamente
    # DEBUG se activa solo en desarrollo para recarga automática y mejor debugging
    app.run(debug=os.getenv("FLASK_ENV") == "development")
```

## 5) Inicializar DB y migraciones

Asegúrate de tener .env completo con tus credenciales antes de correr estos comandos.

```bash
# Windows powershell:
# Activa el entorno virtual
.venv\Scripts\activate

# Configura variables de entorno para Flask
$env:FLASK_APP = "run.py"      # Especifica el archivo principal de la aplicación
$env:FLASK_ENV = "development"  # Configura el entorno como desarrollo

# Inicializa el sistema de migraciones de Alembic
flask db init

# Genera una migración basada en los modelos definidos (crea tabla app_users)
flask db migrate -m "create app_users table"

# Aplica las migraciones a la base de datos (ejecuta los cambios)
flask db upgrade
```

Esto creará la tabla `app_users` con id, username, password_hash en tu base de Supabase

## 6) Ejecutar la app

```bash
# Ejecuta la aplicación Flask
python run.py

# La aplicación estará disponible en:
#  - http://localhost:5000/auth/register  (crear nueva cuenta de usuario)
#  - http://localhost:5000/auth/login     (iniciar sesión con credenciales)
#  - http://localhost:5000/               (página principal protegida - requiere login)
```

**Notas importantes sobre la estructura actualizada:**

1. **Separación de responsabilidades**: Los servicios manejan la lógica de negocio, las rutas solo manejan HTTP
2. **Configuración modular**: Diferentes configuraciones para desarrollo, producción y testing
3. **Blueprints organizados**: Cada funcionalidad tiene su propio blueprint
4. **Extensiones centralizadas**: Todas las extensiones se inicializan en `core/extensions.py`
5. **Manejo de excepciones**: Excepciones personalizadas para mejor control de errores
6. **Templates compartidos**: Los templates están organizados por funcionalidad
7. **Servicios reutilizables**: La lógica de autenticación puede ser reutilizada en otras partes

Esta estructura es más escalable y mantenible que la versión anterior, siguiendo las mejores prácticas de Flask para aplicaciones más grandes.

Puedes ver el código completo en el repositorio [flask-login-demo](https://github.com/Electromayonaise/flask-login-demo.git).
