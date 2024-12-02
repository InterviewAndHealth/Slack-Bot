import logging
import os
from enum import StrEnum

import pandas as pd
import psycopg2

from app import (
    PAYMENT_SERVICE_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USERNAME,
    USER_SERVICE_DB,
)
from app.main import app


class SupportedTables(StrEnum):
    users = "users"
    payments = "payments"


class TableDatabase(StrEnum):
    users = USER_SERVICE_DB
    payments = PAYMENT_SERVICE_DB


class TableColumns(StrEnum):
    users = "public_id, email, userrole, created_at"
    payments = "user_id, customer_email, amount_total, currency, payment_method_types, timestamp, session_id"


TableColumnsAlias: dict[SupportedTables, list[str]] = {
    SupportedTables.users: ["User ID", "Email", "User Role", "Created At"],
    SupportedTables.payments: [
        "User ID",
        "Email",
        "Amount",
        "Currency",
        "Payment Method",
        "Timestamp",
        "Session ID",
    ],
}


@app.command("/get")
async def get(ack, respond, command):
    await ack()

    try:
        table = command.get("text", "").strip()
        if not table:
            return await respond(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Please provide a table name.\nSupported tables: {', '.join([f'`{table.value}`' for table in SupportedTables])}.\n\nExample: `/get users`",
                        },
                    }
                ]
            )
        elif table not in SupportedTables:
            return await respond(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Table `{table}` is not supported.\nSupported tables: {', '.join([f'`{table.value}`' for table in SupportedTables])}.",
                        },
                    }
                ]
            )

        await respond(f"Getting data from `{table}` table...")
        logging.info(f"Getting data from `{table}` table...")

        with psycopg2.connect(
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=TableDatabase[table],
        ) as conn:
            query = f"SELECT {TableColumns[table]} FROM {table}"
            df = pd.read_sql_query(query, conn, dtype=str)
            logging.info(
                f"Data from `{table}` table retrieved successfully. Rows: {len(df)}"
            )

            # Rename columns
            df.columns = TableColumnsAlias[table]

            file_path = f"/tmp/{table}.xlsx"
            df.to_excel(file_path, index=False)
            logging.info(f"Data from `{table}` table saved to {file_path}")

            logging.info(
                f"Uploading data from `{table}` table to Slack channel {command['channel_id']}..."
            )

            # Upload file to Slack
            await app.client.files_upload_v2(
                channel=command["channel_id"],
                file=file_path,
                title=f"{table}.xlsx",
                initial_comment=f"Here is the data from `{table}` table.",
            )
            logging.info(f"Data from `{table}` table uploaded.")
            os.remove(file_path)

    except Exception as e:
        logging.error(f"Error: {e}")
        return await respond(f"❌ Error: {e}")
