import asyncio
from typing import List

from app.deployments import deployments
from app.git import (
    dispatch_workflow,
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
                get_latest_deployments(deployment.deployments, drop_production=True)
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


def sort_deployments(deployments_data: List[Deployment]) -> List[List[Deployment]]:
    # Get recommended deployments
    # If the latest_commit.commit is not the same as the latest_image.commit
    # OR
    # If the latest_version.development is not the same as the latest_image.version
    recommended_deployments = [
        deployment
        for deployment in deployments_data
        if (
            deployment.latest_commit.commit != deployment.latest_image.commit
            or deployment.latest_version.development_version
            != deployment.latest_image.version
        )
    ]

    # Get already updated deployments
    # If the latest_commit.commit is the same as the latest_image.commit
    # AND
    # If the latest_version.development is the same as the latest_image.version
    already_updated_deployments = [
        deployment
        for deployment in deployments_data
        if (
            deployment.latest_commit.commit == deployment.latest_image.commit
            and deployment.latest_version.development_version
            == deployment.latest_image.version
        )
    ]

    return [recommended_deployments, already_updated_deployments]


def get_deployment_checkbox(deployment: Deployment):
    return {
        "text": {"type": "mrkdwn", "text": f"*{deployment.emoji} {deployment.title}*"},
        "description": {
            "type": "mrkdwn",
            "text": f"*Deployed Version:* `{deployment.latest_version.development_version}` at _{format_date(deployment.latest_version.development_date)}_\n*Latest Image:* `{deployment.latest_image.version}` (`{deployment.latest_image.sha()}`)\n*Latest Commit:* `{deployment.latest_commit.sha()}` at _{format_date(deployment.latest_commit.date)}_",
        },
        "value": deployment.id,
    }


@app.command("/dev")
async def dev_deploy(ack, respond, command):
    await ack()

    try:
        deployments_data = await get_deployments_data()
        [recommended_deployments, already_updated_deployments] = sort_deployments(
            deployments_data
        )
    except Exception as e:
        return await respond(f"❌ Error: {e}")

    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚀 Development Deployment",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    if recommended_deployments:
        message_blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🔄 Recommended Updates*\n---"},
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        get_deployment_checkbox(deployment)
                        for deployment in recommended_deployments
                    ],
                    "action_id": "deploy-dev",
                },
            }
        )
        message_blocks.append({"type": "divider"})

    if already_updated_deployments:
        message_blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*✅ Already Updated*\n---"},
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        get_deployment_checkbox(deployment)
                        for deployment in already_updated_deployments
                    ],
                    "action_id": "deploy-dev",
                },
            }
        )
        message_blocks.append({"type": "divider"})

    message_blocks.extend(
        [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔔 *Note:* Select services to deploy to *Development*. Ensure all selections are reviewed before proceeding.",
                    }
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 Deploy to Dev",
                            "emoji": True,
                        },
                        "style": "primary",
                        "action_id": "deploy-dev-button",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Cancel",
                            "emoji": True,
                        },
                        "action_id": "deploy-dev-cancel",
                    },
                ],
            },
        ]
    )

    await respond(blocks=message_blocks)


@app.action("deploy-dev")
async def deploy_dev_action(body, ack, say):
    await ack()


@app.action("deploy-dev-button")
async def deploy_dev_button_action(body, ack, respond):
    await ack()

    selected_options = []
    for value in body["state"]["values"].values():
        selected_options.extend(value["deploy-dev"]["selected_options"])
    selected_services = [option["value"] for option in selected_options]
    selected_deployments = [
        deployment for deployment in deployments if deployment.id in selected_services
    ]
    if not selected_deployments:
        return await respond("❌ No services selected for deployment.")

    results = await asyncio.gather(
        *[
            dispatch_workflow(deployment.repository, deployment.workflows.development)
            for deployment in selected_deployments
        ]
    )

    message_blocks = [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Deploying services to development... 🚀",
                        }
                    ],
                },
                *[
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "text", "text": f"{deployment.emoji} "},
                                    {"type": "text", "text": f"{deployment.title} - "},
                                    {
                                        "type": "link",
                                        "text": "View GitHub Action",
                                        "url": f"https://github.com/{deployment.repository.owner}/{deployment.repository.repo}/actions",
                                    },
                                    {
                                        "type": "text",
                                        "text": " ✅" if result else " ❌",
                                    },
                                ],
                            }
                        ],
                    }
                    for deployment, result in zip(selected_deployments, results)
                ],
            ],
        }
    ]

    await respond(blocks=message_blocks)


@app.action("deploy-dev-cancel")
async def deploy_dev_cancel_action(body, ack, respond):
    await ack()
    await respond("❌ Deployment canceled.")
