from pydantic import BaseModel

from app import (
    DEFAULT_CLUSTER_REPOSITORY,
    DEFAULT_DEVELOPMENT_KUSTOMIZATION,
    DEFAULT_PRODUCTION_KUSTOMIZATION,
    DEFAULT_REPOSITORY_OWNER,
)
from app.models.repository import Repository


class ClusterDeployment(BaseModel):
    repository: Repository = Repository(
        owner=DEFAULT_REPOSITORY_OWNER,
        repo=DEFAULT_CLUSTER_REPOSITORY,
    )

    base_path: str
    development: str
    production: str

    def __init__(
        self,
        base_path: str = None,
        development: str = None,
        production: str = None,
        servive: str = None,
    ):
        if not base_path and not servive:
            raise ValueError(
                "Either base_path or service must be provided to ClusterDeployment"
            )

        if not base_path:
            base_path = f"services/{servive}/overlays"

        super().__init__(
            base_path=base_path,
            development=development or DEFAULT_DEVELOPMENT_KUSTOMIZATION,
            production=production or DEFAULT_PRODUCTION_KUSTOMIZATION,
        )

    def development_path(self) -> str:
        return f"{self.base_path}/{self.development}"

    def production_path(self) -> str:
        return f"{self.base_path}/{self.production}"
