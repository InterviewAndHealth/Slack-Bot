import httpx

from app import GITHUB_TOKEN
from app.models import Headers, Repository


async def dispatch_workflow(
    repo: Repository,
    workflow: str,
) -> bool:
    headers = Headers(
        authorization=GITHUB_TOKEN,
        accept=Headers.ACCEPT.JSON,
    ).to_dict()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches",
            headers=headers,
            json={"ref": repo.branch},
        )
        response.raise_for_status()
        return response.status_code == 204
