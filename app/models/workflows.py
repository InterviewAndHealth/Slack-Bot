from pydantic import BaseModel

from app import DEFAULT_DEVELOPMENT_WORKFLOW, DEFAULT_PRODUCTION_WORKFLOW


class Workflows(BaseModel):
    development: str = DEFAULT_DEVELOPMENT_WORKFLOW
    production: str = DEFAULT_PRODUCTION_WORKFLOW
