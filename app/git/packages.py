import base64
from typing import List

import httpx

from app import GITHUB_TOKEN
from app.models import Headers, LatestImages, Package


# Encode GITHUB_TOKEN
def get_ghcr_token() -> str:
    return base64.b64encode(GITHUB_TOKEN.encode("utf-8")).decode("utf-8")


# Get list of tags
async def get_images(package: Package) -> List[str]:
    ghcr_token = get_ghcr_token()
    headers = Headers(
        authorization=ghcr_token,
        accept=Headers.ACCEPT.V3_JSON,
    ).to_dict()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://ghcr.io/v2/{package}/tags/list",
            headers=headers,
        )
        response.raise_for_status()
        return response.json().get("tags", [])


# Get latest image tags [v0-9, commit hash]
async def get_latest_image(package: Package) -> LatestImages:
    tags = await get_images(package)

    # Filter tags (v0-9)
    version_tags = [tag for tag in tags if tag.startswith("v") and tag[1:].isdigit()]

    # Filter tags (commit hash)
    commit_tags = [tag for tag in tags if len(tag) == 40]

    return LatestImages(
        version=version_tags[-1] if version_tags else None,
        commit=commit_tags[-1] if commit_tags else None,
    )
