import asyncio
from typing import List

from app.deployments import deployments
from app.git import (
    get_latest_commit,
    get_latest_deployments,
    get_latest_image,
)
from app.main import app
from app.models import Deployment
from app.utils import format_date


async def get_deployments_data() -> List[Deployment]:
    deployments_data = deployments.copy()

    [latest_images, latest_commits, latest_versions] = await asyncio.gather(
        asyncio.gather(
            *[get_latest_image(deployment.package) for deployment in deployments_data]
        ),
        asyncio.gather(
            *[
                get_latest_commit(deployment.repository)
                for deployment in deployments_data
            ]
        ),
        asyncio.gather(
            *[
                get_latest_deployments(deployment.deployments)
                for deployment in deployments_data
            ]
        ),
    )

    for deployment, latest_image, latest_commit, deployment_version in zip(
        deployments_data, latest_images, latest_commits, latest_versions
    ):
        deployment.latest_image = latest_image
        deployment.latest_commit = latest_commit
        deployment.latest_version = deployment_version

    return deployments_data


@app.command("/info")
async def info(ack, respond, command):
    await ack()

    try:
        deployments_data = await get_deployments_data()
    except Exception as e:
        return await respond(f"❌ Error: {e}")

    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚀 Deployment Status",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    message_blocks.append(
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"> {deployment.emoji} *{deployment.title}*\n> \n> *Development Version:* \n> `{deployment.latest_version.development_version}` at _{format_date(deployment.latest_version.development_date)}_\n> \n> *Production Version:* \n> `{deployment.latest_version.production_version}` at _{format_date(deployment.latest_version.production_date)}_\n> \n> *Latest Image:* \n> `{deployment.latest_image.version}` (`{deployment.latest_image.sha()}`)\n> \n> *Latest Commit:* \n> `{deployment.latest_commit.sha()}` at _{format_date(deployment.latest_commit.date)}_\n\n-\n",
                }
                for deployment in deployments_data
            ],
        }
    )
    message_blocks.append({"type": "divider"})

    await respond(blocks=message_blocks)
