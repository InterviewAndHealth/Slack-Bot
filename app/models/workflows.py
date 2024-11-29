from pydantic import BaseModel


class Workflows(BaseModel):
    development: str
    production: str
