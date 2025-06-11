from decouple import config
from urllib.parse import quote

class Config:
    user = config("DB_USER")
    password = quote(config("DB_PASS"))
    host = config("DB_HOST")
    port = config("DB_PORT")
    name = config("DB_NAME")

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{name}"