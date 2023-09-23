import os
from pydantic import PostgresDsn

APP_NAME = os.getenv("APP_NAME", "todo-service")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "sraGbRmjYQXmYdnrgPk!OFE35UP6n/QqeoED=iu/bUXBFSSPwnsuprP6T45Qsbwywu2khUka!6IIleY",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30
REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "todo_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "todo_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "todo_db")


PG_URL = PostgresDsn.build(
    scheme="postgresql",
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    path=f"/{POSTGRES_DB}",
)
