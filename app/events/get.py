import datetime
import logging
import os
from enum import StrEnum

from app.main import app
from app.utils import get_payments, get_recruiters, get_students


class SupportedTables(StrEnum):
    students = "students"
    recruiters = "recruiters"
    payments = "payments"


@app.command("/get")
async def get(ack, respond, command):
    await ack()

    try:
        raw_table = command.get("text", "").strip()
        if not raw_table:
            return await respond(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Please provide a table name.\nSupported tables: {', '.join([f'`{table.value}`' for table in SupportedTables])}.\n\nExample: `/get students`\n\nYou can also use substring of the table name. For example, `/get stu`.",
                        },
                    }
                ]
            )

        table = next((t for t in SupportedTables if t.startswith(raw_table)), None)
        if not table:
            return await respond(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Table `{raw_table}` is not supported.\nSupported tables: {', '.join([f'`{table.value}`' for table in SupportedTables])}.",
                        },
                    }
                ]
            )

        await respond(f"Getting data from `{table}` table...")
        logging.info(f"Getting data from `{table}` table...")

        if table == SupportedTables.students:
            (file_name, file_path) = await get_students()
        elif table == SupportedTables.recruiters:
            (file_name, file_path) = await get_recruiters()
        elif table == SupportedTables.payments:
            (file_name, file_path) = await get_payments()

        # Upload file to Slack
        await app.client.files_upload_v2(
            channel=command["channel_id"],
            filename=file_name,
            file=file_path,
            initial_comment=f"Here is the data from `{table}` table ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).",
        )
        logging.info(f"Data from `{table}` table uploaded.")
        os.remove(file_path)

    except Exception as e:
        logging.error(f"Error: {e}")
        return await respond(f"❌ Error: {e}")
