import datetime
import logging

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


async def get_students():
    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        database=USER_SERVICE_DB,
    ) as conn:
        query = "SELECT u.public_id, s.firstname, s.lastname, u.email, s.contactnumber, s.gender, s.city, s.country, u.userrole, u.created_at FROM users u LEFT JOIN students s ON u.public_id = s.userid WHERE u.userrole = 'student';"
        students = pd.read_sql_query(query, conn, dtype=str)
        logging.info(f"`students` retrieved with {len(students)} rows.")

        students.columns = [
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Contact Number",
            "Gender",
            "City",
            "Country",
            "Role",
            "Created At",
        ]

        file_name = f"students_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        file_path = f"/tmp/{file_name}"
        students.to_excel(file_path, index=False)
        logging.info(f"Data from `students` table saved to {file_path}")

        return (file_name, file_path)


async def get_recruiters():
    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        database=USER_SERVICE_DB,
    ) as conn:
        query = "SELECT u.public_id, r.first_name, r.last_name, u.email, r.contact_number, r.company_name, r.company_location, u.userrole, u.created_at FROM users u LEFT JOIN recruiter_profiles r ON u.public_id = r.user_id WHERE u.userrole = 'recruiter';"
        recruiters = pd.read_sql_query(query, conn, dtype=str)
        logging.info(f"`recruiters` retrieved with {len(recruiters)} rows.")

        recruiters.columns = [
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Contact Number",
            "Company Name",
            "Company Location",
            "Role",
            "Created At",
        ]

        file_name = (
            f"recruiters_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        )
        file_path = f"/tmp/{file_name}"
        recruiters.to_excel(file_path, index=False)
        logging.info(f"Data from `recruiters` table saved to {file_path}")

        return (file_name, file_path)


async def get_payments():
    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        database=PAYMENT_SERVICE_DB,
    ) as conn:
        query = "SELECT user_id, customer_email, amount_total, currency, payment_method_types, timestamp, session_id FROM payments;"
        payments = pd.read_sql_query(query, conn, dtype=str)
        logging.info(f"`payments` retrieved with {len(payments)} rows.")

        payments.columns = [
            "User ID",
            "Email",
            "Amount",
            "Currency",
            "Payment Method",
            "Timestamp",
            "Session ID",
        ]

        file_name = f"payments_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        file_path = f"/tmp/{file_name}"
        payments.to_excel(file_path, index=False)
        logging.info(f"Data from `payments` table saved to {file_path}")

        return (file_name, file_path)
