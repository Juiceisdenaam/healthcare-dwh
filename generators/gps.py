import os

import pandas as pd
import psycopg2

from .config import N_GPS
from .faker_instance import fake
from .helpers import introduce_case_noise


def insert_gps_to_postgres(df: pd.DataFrame) -> None:
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
                CREATE TABLE IF NOT EXISTS src.gps (
                    gp_code TEXT PRIMARY KEY,
                    gp_name TEXT NOT NULL,
                    practice_name TEXT NOT NULL,
                    agb_code BIGINT NOT NULL,
                    city TEXT NOT NULL,
                    postal_code TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )

            rows = list(
                df[["gp_code", "gp_name", "practice_name", "agb_code", "city", "postal_code", "created_at"]].itertuples(
                    index=False,
                    name=None,
                )
            )
            cur.executemany(
                """
                INSERT INTO src.gps (gp_code, gp_name, practice_name, agb_code, city, postal_code, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gp_code)
                DO UPDATE SET
                    gp_name = EXCLUDED.gp_name,
                    practice_name = EXCLUDED.practice_name,
                    agb_code = EXCLUDED.agb_code,
                    city = EXCLUDED.city,
                    postal_code = EXCLUDED.postal_code,
                    created_at = EXCLUDED.created_at
                """,
                rows,
            )
        conn.commit()
    finally:
        conn.close()


def generate_gps(n: int = N_GPS, insert_to_postgres: bool = False) -> pd.DataFrame:
    gps = []

    for index in range(n):
        gp_code = f"GP{index + 1:04d}"
        gps.append(
            {
                "gp_code": gp_code,
                "gp_name": introduce_case_noise(fake.name()),
                "practice_name": introduce_case_noise(f"Huisartsenpraktijk {fake.city()}"),
                "agb_code": fake.random_number(digits=8, fix_len=True),
                "city": fake.city(),
                "postal_code": fake.postcode(),
                "created_at": fake.date_time_between("-10y", "now"),
            }
        )

    df = pd.DataFrame(gps)

    if insert_to_postgres:
        insert_gps_to_postgres(df)

    return df