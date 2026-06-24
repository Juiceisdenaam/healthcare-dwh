import random
import os
import re

import numpy as np
import pandas as pd
import psycopg2

from .config import N_PATIENTS
from .faker_instance import fake
from .helpers import (
    generate_initials,
    generate_personal_id,
    generate_policy_number,
    generate_registration_date,
    introduce_name_noise,
    random_birthdate,
    shift_registration_date_to_other_system,
)


def split_house_number(value: str) -> tuple[str, str | None]:
    text = (value or "").strip()
    match = re.match(r"^(\d+)\s*([A-Za-z0-9-]+)?$", text)

    if match:
        return match.group(1), match.group(2)

    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return "1", None

    addition = text.replace(digits, "", 1).strip() or None
    return digits, addition


def generate_house_number_with_noise() -> tuple[str, str | None]:
    """
    Generate realistic house number and addition with occasional human data entry mistakes.
    - ~95%: correct entry (e.g., "120" / "A")
    - ~3%: user entered addition in house_number field, forgot to split (e.g., "120A" / None)
    - ~2%: user entered in both fields (e.g., "120A" / "A")
    """
    base_number = fake.building_number()
    
    # Ensure house number is never 0 or negative
    if not base_number or int(base_number) <= 0:
        base_number = "1"
    
    # Decide if this record has an addition (realistic ~20-30% of addresses have one)
    has_addition = random.random() < 0.25
    
    if not has_addition:
        # No addition - just return the number
        return base_number, None
    
    # Decide the type of data entry
    entry_type = random.choices(
        ["correct", "forgot_to_split", "double_entry"],
        weights=[0.95, 0.03, 0.02],
    )[0]
    
    addition = random.choice(["A", "B", "C", "D", "bis"])
    
    if entry_type == "correct":
        # User properly separated: house_number="120", addition="A"
        return base_number, addition
    
    if entry_type == "forgot_to_split":
        # User entered "120A" in house_number, left addition empty
        return f"{base_number}{addition}", None
    
    if entry_type == "double_entry":
        # User entered "120A" in house_number AND "A" in addition
        return f"{base_number}{addition}", addition
    
    return base_number, addition


def insert_patients_to_postgres(df: pd.DataFrame) -> None:
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
                CREATE TABLE IF NOT EXISTS src.patients (
                    patient_id TEXT PRIMARY KEY,
                    source_system TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    middle_name TEXT,
                    initials TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    birth_date DATE NOT NULL,
                    registration_date TIMESTAMP NOT NULL,
                    email TEXT,
                    phone TEXT,
                    street TEXT NOT NULL,
                    house_number TEXT NOT NULL,
                    house_number_addition TEXT,
                    postal_code TEXT NOT NULL,
                    city TEXT NOT NULL,
                    gp_code TEXT NOT NULL,
                    insurance_code TEXT NOT NULL,
                    policy_number TEXT NOT NULL,
                    personal_identification_number TEXT NOT NULL,
                    original_patient_id TEXT
                );

                ALTER TABLE src.patients
                ADD COLUMN IF NOT EXISTS house_number_addition TEXT
                """
            )

            rows = list(
                df[
                    [
                        "patient_id",
                        "source_system",
                        "first_name",
                        "last_name",
                        "middle_name",
                        "initials",
                        "gender",
                        "birth_date",
                        "registration_date",
                        "email",
                        "phone",
                        "street",
                        "house_number",
                        "house_number_addition",
                        "postal_code",
                        "city",
                        "gp_code",
                        "insurance_code",
                        "policy_number",
                        "personal_identification_number",
                        "original_patient_id",
                    ]
                ].itertuples(index=False, name=None)
            )
            cur.executemany(
                """
                INSERT INTO src.patients (
                    patient_id,
                    source_system,
                    first_name,
                    last_name,
                    middle_name,
                    initials,
                    gender,
                    birth_date,
                    registration_date,
                    email,
                    phone,
                    street,
                    house_number,
                    house_number_addition,
                    postal_code,
                    city,
                    gp_code,
                    insurance_code,
                    policy_number,
                    personal_identification_number,
                    original_patient_id
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (patient_id)
                DO UPDATE SET
                    source_system = EXCLUDED.source_system,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    middle_name = EXCLUDED.middle_name,
                    initials = EXCLUDED.initials,
                    gender = EXCLUDED.gender,
                    birth_date = EXCLUDED.birth_date,
                    registration_date = EXCLUDED.registration_date,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    street = EXCLUDED.street,
                    house_number = EXCLUDED.house_number,
                    house_number_addition = EXCLUDED.house_number_addition,
                    postal_code = EXCLUDED.postal_code,
                    city = EXCLUDED.city,
                    gp_code = EXCLUDED.gp_code,
                    insurance_code = EXCLUDED.insurance_code,
                    policy_number = EXCLUDED.policy_number,
                    personal_identification_number = EXCLUDED.personal_identification_number,
                    original_patient_id = EXCLUDED.original_patient_id
                """,
                rows,
            )
        conn.commit()
    finally:
        conn.close()


def generate_patients(
    gps_df: pd.DataFrame,
    ins_df: pd.DataFrame,
    n: int = N_PATIENTS,
    insert_to_postgres: bool = False,
) -> pd.DataFrame:
    patients = []

    gp_codes = gps_df["gp_code"].tolist()
    insurance_codes = ins_df["insurance_code"].tolist()

    insurance_weights = [0.25, 0.20, 0.18, 0.15, 0.10, 0.05, 0.04, 0.03]
    gp_weights = np.random.dirichlet(np.ones(len(gp_codes)))

    for index in range(n):
        patient_id = f"P{index + 1:07d}"
        first_name = introduce_name_noise(fake.first_name())
        last_name = introduce_name_noise(fake.last_name())
        middle_name = random.choice(["", "", "van", "de", "van der"])
        gender = random.choice(["M", "V"])
        birth_date = random_birthdate()
        registration_date = generate_registration_date(birth_date)
        house_number, house_number_addition = generate_house_number_with_noise()

        patients.append(
            {
                "patient_id": patient_id,
                "source_system": "EPD_A",
                "first_name": first_name,
                "last_name": last_name,
                "middle_name": middle_name,
                "initials": generate_initials(first_name),
                "gender": gender,
                "birth_date": birth_date,
                "registration_date": registration_date,
                "email": fake.email() if random.random() > 0.1 else None,
                "phone": fake.phone_number() if random.random() > 0.1 else None,
                "street": fake.street_name(),
                "house_number": house_number,
                "house_number_addition": house_number_addition,
                "postal_code": fake.postcode(),
                "city": fake.city(),
                "gp_code": random.choices(gp_codes, weights=gp_weights)[0],
                "insurance_code": random.choices(insurance_codes, weights=insurance_weights)[0],
                "policy_number": generate_policy_number(),
                "personal_identification_number": generate_personal_id(),
                "original_patient_id": None,
            }
        )

    df = pd.DataFrame(patients)

    cross_dups = df.sample(frac=0.01, random_state=42).copy()
    cross_dups["original_patient_id"] = cross_dups["patient_id"]
    cross_dups["patient_id"] = [f"P{n + idx + 1:07d}" for idx in range(len(cross_dups))]
    cross_dups["source_system"] = "EPD_B"
    cross_dups["first_name"] = cross_dups["first_name"].apply(introduce_name_noise)
    cross_dups["email"] = None
    cross_dups["registration_date"] = cross_dups["registration_date"].apply(shift_registration_date_to_other_system)

    same_dups = df.sample(frac=0.005, random_state=43).copy()
    same_dups["original_patient_id"] = same_dups["patient_id"]
    same_dups["patient_id"] = [f"P{n + len(cross_dups) + idx + 1:07d}" for idx in range(len(same_dups))]
    same_dups["source_system"] = "EPD_A"
    same_dups["last_name"] = same_dups["last_name"].apply(introduce_name_noise)

    partial_dups = df.sample(frac=0.005, random_state=44).copy()
    partial_dups["original_patient_id"] = partial_dups["patient_id"]
    partial_dups["patient_id"] = [
        f"P{n + len(cross_dups) + len(same_dups) + idx + 1:07d}" for idx in range(len(partial_dups))
    ]
    partial_dups["street"] = partial_dups["street"].apply(lambda _: fake.street_name())
    partial_dups["postal_code"] = fake.postcode()

    false_pos = df.sample(frac=0.005, random_state=45).copy()
    false_pos["original_patient_id"] = None
    false_pos["patient_id"] = [
        f"P{n + len(cross_dups) + len(same_dups) + len(partial_dups) + idx + 1:07d}"
        for idx in range(len(false_pos))
    ]
    false_pos["birth_date"] = false_pos["birth_date"].apply(
        lambda value: value + pd.Timedelta(days=random.randint(-300, 300))
    )
    false_pos["personal_identification_number"] = [generate_personal_id() for _ in range(len(false_pos))]
    false_pos["registration_date"] = false_pos["birth_date"].apply(generate_registration_date)

    result = pd.concat([df, cross_dups, same_dups, partial_dups, false_pos], ignore_index=True)

    if insert_to_postgres:
        insert_patients_to_postgres(result)

    return result