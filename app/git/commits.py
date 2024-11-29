import httpx

from app import GITHUB_TOKEN
from app.models import Headers, LatestCommit, Repository


async def get_latest_commit(repo: Repository) -> LatestCommit:
    headers = Headers(
        authorization=GITHUB_TOKEN,
        accept=Headers.ACCEPT.V3_JSON,
    ).to_dict()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo}/commits/{repo.branch}",
            headers=headers,
            params={"page": 1, "per_page": 1},
        )
        response.raise_for_status()
        return LatestCommit(
            commit=response.json()["sha"],
            date=response.json()["commit"]["committer"]["date"],
        )
