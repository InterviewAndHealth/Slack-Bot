import asyncio
import logging
from typing import List

from app.deployments import deployments
from app.git import dispatch_workflow, get_latest_deployments
from app.main import app
from app.models import Deployment
from app.utils import format_date


async def get_deployments_data() -> List[Deployment]:
    deployments_data = deployments.copy()

    latest_versions = await asyncio.gather(
        *[
            get_latest_deployments(deployment.deployments)
            for deployment in deployments_data
        ]
    )

    for deployment, deployment_versions in zip(deployments_data, latest_versions):
        deployment.latest_version = deployment_versions

    return deployments_data


def sort_deployments(deployments_data: List[Deployment]) -> List[List[Deployment]]:
    # Get recommended deployments
    # If the latest_version.development is not the same as the latest_version.production
    recommended_deployments = [
        deployment
        for deployment in deployments_data
        if deployment.latest_version.development_version
        != deployment.latest_version.production_version
    ]

    # Get already updated deployments
    # If the latest_version.development is the same as the latest_version.production
    updated_deployments = [
        deployment
        for deployment in deployments_data
        if deployment.latest_version.development_version
        == deployment.latest_version.production_version
    ]

    return [recommended_deployments, updated_deployments]


def get_deployment_checkbox(deployment: Deployment):
    return {
        "text": {"type": "mrkdwn", "text": f"*{deployment.emoji} {deployment.title}*"},
        "description": {
            "type": "mrkdwn",
            "text": f"*Development Version:* `{deployment.latest_version.development_version}` at _{format_date(deployment.latest_version.development_date)}_\n*Production Version:* `{deployment.latest_version.production_version}` at _{format_date(deployment.latest_version.production_date)}_",
        },
        "value": deployment.id,
    }


@app.command("/prod")
async def prod_deploy(ack, respond, command):
    await ack()
    logging.info("Acknowledged /prod command")

    try:
        deployments_data = await get_deployments_data()
        [recommended_deployments, already_updated_deployments] = sort_deployments(
            deployments_data
        )
    except Exception as e:
        logging.error(f"Error fetching deployments data: {e}")
        return await respond(f"Error: {e}")

    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚀 Production Deployment",
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
                    "action_id": "deploy-prod",
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
                    "action_id": "deploy-prod",
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
                        "text": "🔔 *Note:* Select services to deploy to *Production*. Ensure all selections are reviewed before proceeding.",
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
                            "text": "🚀 Deploy to Prod",
                            "emoji": True,
                        },
                        "style": "primary",
                        "action_id": "deploy-prod-button",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Cancel",
                            "emoji": True,
                        },
                        "action_id": "deploy-prod-cancel",
                    },
                ],
            },
        ]
    )

    await respond(blocks=message_blocks)


@app.action("deploy-prod")
async def deploy_prod_action(body, ack, say):
    await ack()


@app.action("deploy-prod-button")
async def deploy_prod_button_action(body, ack, respond):
    await ack()

    selected_options = []
    for value in body["state"]["values"].values():
        selected_options.extend(value["deploy-prod"]["selected_options"])
    selected_services = [option["value"] for option in selected_options]
    selected_deployments = [
        deployment for deployment in deployments if deployment.id in selected_services
    ]
    if not selected_deployments:
        return await respond("❌ No services selected for deployment.")

    logging.info(
        f"Deploy to Production: {[deployment.title for deployment in selected_deployments]}"
    )

    results = await asyncio.gather(
        *[
            dispatch_workflow(deployment.repository, deployment.workflows.production)
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
                            "text": "Deploying services to production... 🚀",
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


@app.action("deploy-prod-cancel")
async def deploy_prod_cancel_action(body, ack, respond):
    await ack()
    await respond("❌ Deployment canceled.")
