import os

import pandas as pd
import psycopg2


def insert_insurances_to_postgres(df: pd.DataFrame) -> None:
    dbname = os.getenv("PG_DB")
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASSWORD")

    if not dbname or not user or not password:
        raise ValueError("PG_DB, PG_USER and PG_PASSWORD environment variables are required")

    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=dbname,
        user=user,
        password=password,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE SCHEMA IF NOT EXISTS src;
                CREATE TABLE IF NOT EXISTS src.insurances (
                    insurance_code TEXT PRIMARY KEY,
                    insurance_name TEXT NOT NULL
                )
                """
            )

            rows = list(df[["insurance_code", "insurance_name"]].itertuples(index=False, name=None))
            cur.executemany(
                """
                INSERT INTO src.insurances (insurance_code, insurance_name)
                VALUES (%s, %s)
                ON CONFLICT (insurance_code)
                DO UPDATE SET insurance_name = EXCLUDED.insurance_name
                """,
                rows,
            )
        conn.commit()
    finally:
        conn.close()


def generate_insurances(insert_to_postgres: bool = False) -> pd.DataFrame:
    insurances = [
        ("CZ", "CZ"),
        ("VGZ", "VGZ"),
        ("ZK", "Zilveren Kruis"),
        ("MEN", "Menzis"),
        ("DSW", "DSW"),
        ("NN", "Nationale-Nederlanden"),
        ("ONVZ", "ONVZ"),
        ("ASR", "a.s.r."),
    ]
    df = pd.DataFrame(insurances, columns=["insurance_code", "insurance_name"])

    if insert_to_postgres:
        insert_insurances_to_postgres(df)

    return df
    