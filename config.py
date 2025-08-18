import os
from urllib.parse import quote_plus

def build_db_uri():
    # Prioriza DATABASE_URL (útil en despliegues)
    url = os.getenv("DATABASE_URL")
    if url:
        # Garantiza sslmode=require si no está presente
        return url if "sslmode=" in url else (url + ("&" if "?" in url else "?") + "sslmode=require")

    # Construye desde piezas SUPABASE_*
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

    # Opcional: engine tuning
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        # Con psycopg2, ssl ya va en la URL; esto es redundante pero seguro:
        "connect_args": {"sslmode": "require"},
    }

    # Por si luego usamos el SDK de Supabase o REST
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    