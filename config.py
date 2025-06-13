from decouple import config
from urllib.parse import quote

class Config:
    """
    Configuration class for the Flask application.

    Loads settings from environment variables using `python-decouple`.

    Environment variables required:
        - DEBUG: Whether to run in debug mode (bool).
        - DB_USER: Username for the PostgreSQL database.
        - DB_PASS: Password for the database (URL-encoded automatically).
        - DB_HOST: Hostname of the database.
        - DB_PORT: Port number for the database.
        - DB_NAME: Name of the database.

    Configures:
        - SQLALCHEMY_DATABASE_URI: Full PostgreSQL connection string.
        - SQLALCHEMY_TRACK_MODIFICATIONS: Disables modification tracking.
    """
    DEBUG = config('DEBUG', default=True, cast=bool)
    user = config("DB_USER")
    password = quote(config("DB_PASS"))
    host = config("DB_HOST")
    port = config("DB_PORT")
    name = config("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@{host}:{port}/{name}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False