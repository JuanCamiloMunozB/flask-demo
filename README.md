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
flask-demo/
  app/
    auth/                # registro/login + templates
    bot/                 # UI del bot + modelos bayesianos y experto
    extensions.py        # db, migrate, login_manager, bcrypt
    models.py            # User, ChatSession, ChatMessage
  migrations/            # Alembic
  tests/                 # unit, integration, stress, validation
  config.py              # Config y construcción de DB URI
  run.py                 # Punto de entrada

```

## Configuración de entorno 

El archivo config.py permite dos rutas:

1. DATABASE_URL (recomendada en despliegues): si está presente, se usa tal cual y fuerza sslmode=require si falta.

2. Variables SUPABASE_* para construir la URI:
`SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`.
Además, define `SECRET_KEY` y opciones del engine.

### Ejemplo.env 

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



# Instrucciones para crear el apartado de login con las tecnologías de flask

Objetivo: levantar un mini-proyecto vacío con registro, login, logout usando Flask, Flask-Login, Flask-WTF, SQLAlchemy, Flask-Migrate y PostgreSQL de Supabase. Incluye estructura de carpetas, archivos listos para copiar/pegar, variables de entorno, migraciones y comandos para ejecutar.

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

## 3) Estructura mínima

```bash
flask-login-demo/
  app/
    auth/
      static/css/style.css      
      templates/
        login.html              
        register.html
        dashboard.html           
      __init__.py               # Blueprint 'auth'
      forms.py                  # Flask-WTF forms
      routes.py                 # Rutas /register, /login, /logout (+ dashboard)
    __init__.py                 # create_app, extensiones y login_manager
    extensions.py               # db, migrate, login_manager, bcrypt
    models.py                   # User (mismos campos y hash)
  migrations/                   # Se creará al correr 'flask db init'
  config.py                     # Construcción de la DB URI (Supabase)
  .env                          # Credenciales
  run.py                        # Entry point (carga .env y arranca Flask)

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
from urllib.parse import quote_plus

def build_db_uri():
    url = os.getenv("DATABASE_URL")
    if url:
        return url if "sslmode=" in url else (url + ("&" if "?" in url else "?") + "sslmode=require")
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    pwd = quote_plus(os.getenv("SUPABASE_DB_PASSWORD", ""))
    host = os.getenv("SUPABASE_DB_HOST", "localhost")
    port = os.getenv("SUPABASE_DB_PORT", "5432")
    name = os.getenv("SUPABASE_DB_NAME", "postgres")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}?sslmode=require"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"},
    }
```

### 4.3 app/extensions.py

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
```

### 4.4 app/models.py

```python
# app/models.py
from flask_login import UserMixin
from .extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'app_users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)
```

### 4.5 app/__init__.py (App factory)

Aquí es donde cambiamos la redirección post-login: si el user está autenticado, iremos a /dashboard (placeholder), no al chatbot pues estas instrucciones serían muy largas con el chatbot. El resto permanece igual.

```python
# app/__init__.py
from flask import Flask, redirect, url_for
from flask_login import current_user
from .auth import auth
from .auth.extensions import db, migrate, login_manager, bcrypt
from .auth.models import User

def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'auth.login'

    # SOLO el blueprint de auth en este mini-setup
    app.register_blueprint(auth, url_prefix="/auth")

    # user_loader (¡imprescindible para Flask-Login!)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Raíz: si está logueado → dashboard; si no → login
    @app.route('/')
    def root():
        if current_user.is_authenticated:
            return redirect(url_for('auth.dashboard'))
        return redirect(url_for('auth.login'))

    return app
```

### 4.6 app/auth/__init__.py

```python
# app/auth/__init__.py
from flask import Blueprint
auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")
from . import routes  # noqa
```
### 4.7 app/auth/forms.py


```python
# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from ..auth.models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already in use')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```

### 4.8 app/auth/routes.py

```python
# app/auth/routes.py
# app/auth/routes.py
from flask import request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from . import auth
from ..auth.forms import RegisterForm, LoginForm
from ..auth.extensions import db
from ..auth.models import User

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append('El nombre de usuario ya existe')
                return render_template('register.html', form=form), 400
            return redirect(url_for('auth.login'))
        return render_template('register.html', form=form), 400
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('auth.dashboard'))   # <-- cambio necesario
            form.password.errors.append('Credenciales inválidas')
            return render_template('login.html', form=form), 401
        return render_template('login.html', form=form), 400
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)  # placeholder
```

### 4.9 app/auth/templates/register.html

```html
<!-- app/auth/templates/register.html -->
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
        {% for err in form.username.errors %}
          <div class="text-danger small">{{ err }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.password.label(class_='form-label') }}
        {{ form.password(class_='form-control input-dark', placeholder='Contraseña') }}
        {% for err in form.password.errors %}
          <div class="text-danger small">{{ err }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.confirm.label(class_='form-label') }}
        {{ form.confirm(class_='form-control input-dark', placeholder='Confirma la contraseña') }}
        {% for err in form.confirm.errors %}
          <div class="text-danger small">{{ err }}</div>
        {% endfor %}
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

### 4.10 app/auth/templates/login.html

```html
<!-- app/auth/templates/login.html -->
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

      {# Top-level error alert: muestra todos los mensajes de error del formulario #}
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
        {% for err in form.username.errors %}
          <div class="text-danger small">{{ err }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.password.label(class_='form-label') }}
        {{ form.password(class_='form-control input-dark', placeholder='Contraseña') }}
        {% for err in form.password.errors %}
          <div class="text-danger small">{{ err }}</div>
        {% endfor %}
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

### 4.11 app/auth/templates/dashboard.html

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
      <p class="mb-3">Bienvenido, <span class="text-accent">{{ username }}</span>.</p>
      <a class="btn btn-secondary" href="{{ url_for('auth.logout') }}">Cerrar sesión</a>
    </div>
  </div>
</body>
</html>
```

### 4.12 app/auth/static/css/style.css

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
  to { transform: rotate(360deg); }
}

```

### 4.12 run.py

```python
# run.py
import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()
app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_ENV") == "development")
```

## 5) Inicializar DB y migraciones

Asegúrate de tener .env completo con tus credenciales antes de correr estos comandos.

```bash
# Windows powershell:
.venv\Scripts\activate
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"

# Crear carpeta de migraciones
flask db init

# Generar migración desde el modelo 'User' (tabla app_users)
flask db migrate -m "create app_users table"

# Aplicar migraciones
flask db upgrade
```

Esto creará la tabla users con id, username, password_hash en tu base de Supabase

## 6) Ejecutar la app

```bash
python run.py
# Navega a:
#  - http://localhost:5000/register  (para crear usuario)
#  - http://localhost:5000/login     (para iniciar sesión)
#  - http://localhost:5000/dashboard (protegido; requiere login)
```
