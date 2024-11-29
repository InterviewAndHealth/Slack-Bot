from pydantic import BaseModel


class DeploymentVersion(BaseModel):
    development_version: str | None
    production_version: str | None

    development_date: str | None
    production_date: str | None

    def __str__(self) -> str:
        return f"production: {self.production_version}, development: {self.development_version}"
