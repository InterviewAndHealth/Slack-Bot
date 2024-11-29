import asyncio
import re
from typing import List

import httpx

from app import GITHUB_TOKEN
from app.models import ClusterDeployment, DeploymentVersion, Headers, Repository


async def get_deployment_tag(
    repo: Repository,
    file_path: str,
) -> str | None:
    headers = Headers(
        authorization=GITHUB_TOKEN,
        accept=Headers.ACCEPT.RAW_JSON,
    ).to_dict()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo}/contents/{file_path}",
            headers=headers,
            params={"ref": repo.branch},
        )
        response.raise_for_status()
        content = response.text

    match = re.search(r"newTag: (\w+)", content)
    if not match:
        return None
    return match.group(1)


async def get_deployment_date(
    repo: Repository,
    file_path: str,
) -> str | None:
    headers = Headers(
        authorization=GITHUB_TOKEN,
        accept=Headers.ACCEPT.RAW_JSON,
    ).to_dict()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo}/commits",
            headers=headers,
            params={"path": file_path, "page": 1, "per_page": 1},
        )
        response.raise_for_status()
        content = response.json()

        return content[0]["commit"]["committer"]["date"]


async def get_deployment(repo: Repository, file_path: str) -> List[str]:
    [tag, date] = await asyncio.gather(
        get_deployment_tag(repo, file_path),
        get_deployment_date(repo, file_path),
    )
    return [tag, date]


async def fake_get_deployment() -> List[None]:
    return [None, None]


async def get_latest_deployments(
    deployment: ClusterDeployment,
    drop_development: bool = False,
    drop_production: bool = False,
) -> DeploymentVersion:
    [development, production] = await asyncio.gather(
        (
            get_deployment(deployment.repository, deployment.development_path())
            if not drop_development
            else fake_get_deployment()
        ),
        (
            get_deployment(deployment.repository, deployment.production_path())
            if not drop_production
            else fake_get_deployment()
        ),
    )

    return DeploymentVersion(
        development_version=development[0],
        production_version=production[0],
        development_date=development[1],
        production_date=production[1],
    )
