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

DEFAULT_PACKAGE_USERNAME = os.environ.get(
    "DEFAULT_PACKAGE_USERNAME", "interviewandhealth"
)
DEFAULT_REPOSITORY_OWNER = os.environ.get(
    "DEFAULT_REPOSITORY_OWNER", "InterviewAndHealth"
)
DEFAULT_BRANCH = os.environ.get("DEFAULT_BRANCH", "main")
DEFAULT_CLUSTER_REPOSITORY = os.environ.get("DEFAULT_CLUSTER_REPOSITORY", "Cluster")
DEFAULT_DEVELOPMENT_WORKFLOW = os.environ.get(
    "DEFAULT_DEVELOPMENT_WORKFLOW", "build.yml"
)
DEFAULT_PRODUCTION_WORKFLOW = os.environ.get(
    "DEFAULT_PRODUCTION_WORKFLOW", "deploy.yml"
)
DEFAULT_DEVELOPMENT_KUSTOMIZATION = os.environ.get(
    "DEFAULT_DEVELOPMENT_KUSTOMIZATION", "development/kustomization.yaml"
)
DEFAULT_PRODUCTION_KUSTOMIZATION = os.environ.get(
    "DEFAULT_PRODUCTION_KUSTOMIZATION", "production/kustomization.yaml"
)

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
