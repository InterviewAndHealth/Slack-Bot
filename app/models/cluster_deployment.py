from pydantic import BaseModel

from app.models.repository import Repository


class ClusterDeployment(BaseModel):
    repository: Repository
    base_path: str
    development: str
    production: str

    def development_path(self) -> str:
        return f"{self.base_path}/{self.development}"

    def production_path(self) -> str:
        return f"{self.base_path}/{self.production}"
