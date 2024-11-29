import os

from dotenv import load_dotenv

load_dotenv(override=True)

HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", 8000)
ENV = os.environ.get("ENV", "production")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

USER_SERVICE_DB = os.environ.get("USER_SERVICE_DB", "users_db")
PAYMENT_SERVICE_DB = os.environ.get("PAYMENT_SERVICE_DB", "payments_db")

_imported_variable = {
    "PORT": PORT,
    "BOT_TOKEN": BOT_TOKEN,
    "SIGNING_SECRET": SIGNING_SECRET,
    "GITHUB_TOKEN": GITHUB_TOKEN,
    "POSTGRES_USERNAME": POSTGRES_USERNAME,
    "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
    "POSTGRES_HOST": POSTGRES_HOST,
    "POSTGRES_PORT": POSTGRES_PORT,
}

if not all(_imported_variable.values()):
    missing_variables = [key for key, value in _imported_variable.items() if not value]
    raise ValueError(f"Missing environment variables: {missing_variables}")

PORT = int(PORT)
