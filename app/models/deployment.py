from pydantic import BaseModel

from app.models.cluster_deployment import ClusterDeployment
from app.models.deployment_version import DeploymentVersion
from app.models.latest_commit import LatestCommit
from app.models.latest_images import LatestImages
from app.models.package import Package
from app.models.repository import Repository
from app.models.workflows import Workflows


class Deployment(BaseModel):
    id: str
    title: str
    emoji: str
    package: Package
    repository: Repository
    workflows: Workflows
    deployments: ClusterDeployment

    latest_image: LatestImages = None
    latest_commit: LatestCommit = None
    latest_version: DeploymentVersion = None
