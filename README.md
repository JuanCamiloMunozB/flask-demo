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
        routes.py                 # Rutas /register, /login, /logout, /dashboard
    config/
      base.py                     # Configuración base y construcción de DB URI
      development.py              # Configuración de desarrollo
    core/
      exceptions.py               # Excepciones personalizadas
      extensions.py               # db, migrate, login_manager, bcrypt
    models/
      user.py                     # Modelo User
    services/
      auth_service.py             # Lógica de autenticación
    templates/
      auth/
        dashboard.html            # Dashboard del usuario
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
from app.config.base import Config as BaseConfig
from app.config.development import DevelopmentConfig

# Con esta configuración, puedes fácilmente cambiar entre diferentes entornos simplemente
# modificando la variable de entorno FLASK_ENV. Por defecto, se usará la configuración
# de desarrollo si no se especifica otra.

# En esta guia, trabajaremos con DevelopmentConfig.

# from app.config.production import ProductionConfig
# from app.config.testing import TestingConfig

Config = BaseConfig

config = {
    'development': DevelopmentConfig,
    'default': Config
    # 'production': ProductionConfig,
    # 'testing': TestingConfig,
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'default') # Se usa 'default' si no se define FLASK_ENV
    return config.get(env, Config)
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

# Flask nos permite definir configuraciones mediante clases. 
# En este caso, usamos una clase base y luego podemos extenderla para
# diferentes entornos (desarrollo, producción, testing, etc.).

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


# Para poder usar las extensiones, debemos inicializarlas con la app. 
# Esto se hace en una función aparte para mantener el código limpio.
def init_extensions(app):
    """Initialize Flask extensions with the app instance."""
    # Vincula todas las extensiones con la instancia de Flask
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Para que el login manager funcione correctamente, necesitamos
    # definir algunas configuraciones y funciones adicionales.

    # Establece la ruta por defecto a la que se redirige cuando un usuario no autenticado intenta acceder a una página protegida.
    # Aquí, 'auth.login' es el endpoint del blueprint de autenticación donde se maneja el login. Donde 'auth' es el nombre del blueprint y 'login' es la función de vista.
    login_manager.login_view = 'auth.login'

    # Esta función se utiliza por Flask-Login para cargar un usuario desde la base de datos usando su ID.
    # El decorador @login_manager.user_loader indica que esta función será llamada automáticamente por Flask-Login.
    # Se importa el modelo User y se busca el usuario por su ID usando la consulta User.query.get(int(user_id)).
    # Si el usuario existe, se retorna el objeto User; si no, retorna None.
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
```

### 4.6 app/models/user.py

```python
# app/models/user.py
from flask_login import UserMixin
from app.core.extensions import db, bcrypt

# La clase User representa a un usuario en la base de datos para autenticación.
# Hereda de UserMixin (para integración con Flask-Login) y db.Model (para ORM de SQLAlchemy).
# UserMixin proporciona métodos y propiedades estándar (como is_authenticated, is_active, get_id) 
# necesarios para la gestión de sesiones y autenticación de usuarios en Flask-Login.
# db.Model permite mapear la clase User a una tabla de la base de datos usando SQLAlchemy, 
# facilitando operaciones CRUD y la persistencia de datos de usuario.
class User(UserMixin, db.Model):
    """User model for authentication."""
    # Nombre específico de tabla para evitar conflictos con 'users' reservado
    __tablename__ = 'app_users'
    
    # Campos de la tabla (Columnas)
    # SQLAlchemy nos permite definir las columnas de la tabla como atributos de la clase y especificar sus tipos y restricciones.
    # En este caso, tenemos:
    
    # El campo id es una columna de tipo entero, actúa como clave primaria y se autoincrementa automáticamente.
    id = db.Column(db.Integer, primary_key=True)

    # El campo username es una columna de tipo cadena (String) con una longitud máxima de 80 caracteres, debe ser único (unique) y no puede ser nulo (nullable=False).
    # Esto es porque el nombre de usuario es el identificador principal para login, lo que implica que no puede haber dos usuarios con el mismo nombre o que esté vacío.
    username = db.Column(db.String(80), unique=True, nullable=False)

    # El campo password_hash es una columna de tipo cadena (String) con una longitud máxima de 128 caracteres, no puede ser nulo.
    # Aquí almacenamos el hash seguro de la contraseña, nunca la contraseña en texto plano, lo que es crucial para la seguridad.
    password_hash = db.Column(db.String(128), nullable=False)

    # El método set_password genera un hash seguro de la contraseña usando bcrypt,
    # nunca almacena la contraseña en texto plano, lo que protege contra robos de datos.
    def set_password(self, password: str):
        """Set the user's password hash."""
        # Genera hash seguro de la contraseña usando bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # El método check_password verifica si una contraseña dada coincide con el hash almacenado,
    # permitiendo autenticación segura sin exponer la contraseña original.
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
    
    # La función `register_user` verifica si el nombre de usuario ya existe en la base de datos, 
    # y si no existe, crea un nuevo usuario con la contraseña hasheada para mayor seguridad. 
    @staticmethod
    def register_user(username: str, password: str) -> User:
        """Register a new user."""
        # Verifica si el usuario ya existe en la base de datos
        # SQLAlchemy nos permite hacer consultas de manera sencilla usando el modelo User, sin la necesidad de escribir SQL directamente.
        # En este caso, usamos filter_by para buscar un usuario con el mismo nombre.
        if User.query.filter_by(username=username).first():
            raise AuthenticationError("Username already exists")
        
        # Crea un nuevo usuario con contraseña hasheada
        user = User(username=username)
        user.set_password(password)  # Aqui llamamos al método del modelo User que genera el hash seguro
        
        # Guarda el usuario en la base de datos
        db.session.add(user)
        db.session.commit()
        return user
    
    # La función `authenticate_user` busca el usuario por nombre de usuario y valida la contraseña 
    # utilizando el método seguro definido en el modelo de usuario. Si las credenciales no son válidas, 
    # lanza una excepción personalizada de autenticación.
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

# Colocamos esta factory en __init__.py porque en Python ese archivo marca el directorio
# como paquete y suele usarse como punto de entrada del paquete. Exportar create_app
# desde app.__init__ permite hacer "from app import create_app" y mantiene la inicialización
# y el registro de componentes (extensiones, blueprints, rutas) en un único lugar.

def create_app(config_object=None):
    # Crear y configurar la aplicación Flask (Application Factory)
    # - Patrón recomendado en Flask: una función que crea y devuelve la app.
    # - Permite crear varias instancias con distinta configuración (tests, dev, prod).
    # - Evita importaciones circulares porque la app se crea bajo demanda.
    app = Flask(__name__)
    
    # Cargar la configuración correcta
    # - Si no se pasa explicitamente un objeto de configuración, se obtiene según entorno.
    # - app.config.from_object carga solo atributos en MAYÚSCULAS de la clase/ módulo.
    #   Esto convierte constantes de configuración en valores usados por Flask y extensiones.
    if config_object is None:
        from config import get_config
        config_object = get_config()
    app.config.from_object(config_object)
    
    # Inicializar extensiones con la app (db, migrate, login_manager, bcrypt, ...)
    init_extensions(app)
    
    # Registrar blueprints (módulos de rutas)
    # - Los blueprints agrupan rutas y recursos (p. ej. auth) y permiten prefijos de URL y
    #   reutilización/registro múltiple si fuera necesario.
    # - Registrar en el factory centraliza la estructura de la app al iniciarse.
    app.register_blueprint(auth, url_prefix="/auth")
    
    # Ruta raíz: comportamiento según estado de autenticación
    # - current_user es un proxy de Flask-Login que solo funciona dentro del contexto de petición.
    # - Si el usuario está autenticado, redirigimos a su dashboard; si no, redirigimos al login.
    # - url_for genera la URL del endpoint 'auth.login' (requiere contexto; aquí se invoca durante la petición).
    @app.route('/')
    def root():
        # Si el usuario está autenticado, mostrar bienvenida
        if current_user.is_authenticated:
            return redirect(url_for('auth.dashboard'))
        # Si no está autenticado, redirigir al endpoint de login del blueprint 'auth'
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

# Formulario de registro y login usando Flask-WTF y WTForms.
# Estas librerias nos permite crear formularios web con clases de Python, sin necesidad de escribir HTML manualmente.
# - WTForms: biblioteca independiente que define campos, validadores y lógica de formularios en Python (Field, StringField, PasswordField, validators, etc.). No depende de Flask.
# - Flask-WTF: extensión para Flask que integra WTForms con la app Flask. Añade CSRF automático, helpers como FlaskForm, validate_on_submit(), soporte para reCAPTCHA y configuración vía app.config, y simplifica obtener datos de request/form.
# - En práctica: usas WTForms para los campos/validators y Flask-WTF para integrarlo en Flask.
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

    # Esta función es un validador personalizado para WTForms y se ejecuta automáticamente cuando existe
    # un método con el nombre validate_<fieldname> (aquí validate_username) durante la llamada a
    # form.validate(). No es necesario llamarla explícitamente.
    def validate_username(self, username):
        """Validate that username is unique."""
        # verifica que el username no exista
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
from flask_login import current_user, login_user, logout_user, login_required
from . import auth
from .forms import RegisterForm, LoginForm
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError

# Este archivo define las rutas del blueprint "auth".
# En Flask los blueprints agrupan funcionalidad relacionada (aquí: autenticación)
# y se registran en la app principal desde la fábrica de aplicaciones.
# Esto ayuda a organizar el código y facilita pruebas e importaciones.

# Se importan los formularios WTForms (RegisterForm, LoginForm). WTForms
# proporciona validación y, si está configurado, protección CSRF.
# En las vistas se usa form.validate_on_submit() que combina comprobar
# que la petición es POST y que los validadores pasan correctamente.

# La lógica de negocio de autenticación se delega a AuthService.
# Las vistas actúan como controladores ligeros: validan entrada, orquestan
# llamadas al servicio y retornan respuestas HTTP (templates / redirects).
# Esto sigue el principio de separación de responsabilidades.

# Uso de flash(): Flask almacena mensajes en la sesión para mostrarlos
# en la siguiente renderización. Es útil para feedback tras un redirect.

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = RegisterForm()
    
    # GET: mostrar formulario vacío.
    # POST: procesar datos enviados. validate_on_submit() maneja
    # tanto la comprobación de método como la validación del formulario.
    if request.method == 'POST':
        # Si el formulario es válido (pasa todas las validaciones)
        if form.validate_on_submit():
            try:
                # Delegamos el registro al servicio AuthService.
                # AuthService encapsula la lógica de negocio (persistencia, validaciones).
                user = AuthService.register_user(form.username.data, form.password.data)
                # Post/Redirect/Get: después de un POST exitoso se redirige
                # para evitar reenvío de formularios al recargar la página.
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except AuthenticationError as e:
                # Traducción de errores de negocio a mensajes para el usuario.
                # Ejemplo: usuario ya existe.
                flash(str(e), 'error')
        # Si hay errores de validación, re-renderiza con errores y código 400.
        # Las plantillas deberían mostrar form.errors para feedback.
        return render_template('register.html', form=form), 400
    
    # GET request: muestra formulario vacío (código 200 implícito)
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    
    # Similar patrón: GET muestra formulario; POST procesa credenciales.
    if request.method == 'POST':
        # validate_on_submit() comprueba POST + validadores (incl. CSRF).
        if form.validate_on_submit():
            try:
                # AuthService realiza la autenticación y devuelve el usuario.
                user = AuthService.authenticate_user(form.username.data, form.password.data)
                # Flask-Login: marca al usuario como autenticado en la sesión.
                login_user(user)
                flash('Login successful!', 'success')
                # Redirige a la raíz (Post/Redirect/Get).
                return redirect(url_for('root'))
            except AuthenticationError as e:
                # Credenciales inválidas traducidas a mensaje visible.
                flash(str(e), 'error')
        # Errores de validación o autenticación -> re-render + 400.
        return render_template('login.html', form=form), 400
    
    # GET request: muestra formulario de login
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required  # Protege la ruta: sólo accesible si el usuario está autenticado.
def logout():
    """Logout the current user."""
    # Flask-Login: termina la sesión/estado de autenticación del usuario.
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@login_required
def dashboard():
    # Página protegida que solo usuarios autenticados pueden ver.
    return render_template('dashboard.html', username=current_user.username)
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
  <link rel="stylesheet" href="{{ url_for('auth.static', filename='css/style.css') }}" />
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
  <link rel="stylesheet" href="{{ url_for('auth.static', filename='css/style.css') }}" />
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

### 4.15 app/templates/auth/dashboard.html

```html
<!-- app/auth/templates/dashboard.html -->
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('auth.static', filename='css/style.css') }}" />
</head>
<body>
    <div class="chat-container d-flex flex-column">
        <div class="chat-header">
            <div class="title"><strong>Dashboard</strong></div>
        </div>
        <div class="chat-body p-4">
            <div class="mb-3">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                            {{ message }}
                        </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            <p class="mb-3">Bienvenido, <span class="text-accent">{{ username }}</span>.</p>
            <a class="btn btn-secondary" href="{{ url_for('auth.logout') }}">Cerrar sesión</a>
        </div>
    </div>
</body>
</html>
```

### 4.16 app/static/css/style.css

```css
/* app/auth/static/css/style.css */
body {
    background-color: #121212;
    font-family: 'Segoe UI', sans-serif;
    color: #e0e0e0;
}

.chat-container {
    max-width: 600px;
    margin: 2rem auto;
    background-color: #1e1e1e;
    border-radius: 16px;
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    height: 85vh;
}

.chat-header {
    background-color: #1a1a1a;
    padding: 1rem;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    border-bottom: 1px solid #2e2e2e;
}

.title {
    font-size: 1.2rem;
    color: #cc444b;
}

.text-accent {
    color: #cc444b;
}

.chat-body {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
}

.message {
    margin-bottom: 1rem;
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 20px;
    line-height: 1.5;
    font-size: 0.95rem;
}

.message.user {
    background-color: #2c2c2c;
    align-self: flex-end;
    text-align: right;
    color: #e0e0e0;
}

.message.bot {
    background-color: #cc444b;
    color: #e0e0e0;
    border-left: 4px solid #cc444b;
    align-self: flex-start;
}


.chat-footer {
    padding: 1rem;
    border-top: 1px solid #2e2e2e;
    display: flex;
    flex-direction: column;
}

.input-dark {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: none;
    border-radius: 10px 0 0 10px;
}

.input-dark::placeholder {
    color: #888;
}

.input-dark:focus {
    color: #cc444b;
    outline: none;
    box-shadow: 0 0 0 2px rgba(204, 68, 75, 0.4);
    background-color: #2a2a2a;
}

.send-btn {
    background-color: #cc444b;
    color: #fff;
    border: none;
    border-radius: 0 10px 10px 0;
    transition: background-color 0.3s;
}

.send-btn:hover {
    background-color: #a9383e;
}

.sport-btn {
    background-color: transparent;
    color: #cc444b;
    border: 1px solid #cc444b;
    border-radius: 30px;
    padding: 0.5rem 1.2rem;
    transition: background-color 0.3s, color 0.3s;
}

.sport-btn:hover {
    background-color: #cc444b;
    color: #fff;
}

.restart-btn {
    background-color: #333;
    color: #cc444b;
    border-radius: 30px;
    border: 1px solid #cc444b;
    transition: background-color 0.3s, color 0.3s;
}

.restart-btn:hover {
    background-color: #cc444b;
    color: #fff;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
    background-color: #cc444b;
    border-radius: 10px;
    border: 2px solid #1a1a1a;
}

* {
    scrollbar-width: thin;
    scrollbar-color: #cc444b #1a1a1a;
}

@media (max-width: 768px) {
    .chat-container {
        height: 95vh;
        border-radius: 0;
    }
}


.spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 3px solid #ccc;
    border-top: 3px solid #333;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 5px;
    vertical-align: middle;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
```

### 4.17 run.py

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
#  - http://localhost:5000/auth/dashboard (dashboard del usuario autenticado)
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

Puedes ver el código completo en el repositorio [flask-login-demo](https://github.com/JuanCamiloMunozB/flask-login-demo).
