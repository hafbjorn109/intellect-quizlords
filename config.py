from decouple import config
from urllib.parse import quote

class Config:
    user = config("DB_USER")
    password = quote(config("DB_PASS"))
    host = config("DB_HOST")
    port = config("DB_PORT")
    name = config("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@{host}:{port}/{name}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False