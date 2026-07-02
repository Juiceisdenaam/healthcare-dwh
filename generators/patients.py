import random
import os
import re
from datetime import timedelta

import numpy as np
import pandas as pd
import psycopg2

from .config import (
    CROSS_SOURCE_VARIANT_RATES,
    FALSE_POSITIVE_RATES,
    INTRA_SOURCE_DUP_RATES,
    N_PATIENTS,
    SOURCE_NOISE_PROFILES,
    SOURCE_OVERLAP_DISTRIBUTION,
    SOURCE_PAIR_WEIGHTS,
    SOURCE_SYSTEMS,
    SOURCE_VOLUME_WEIGHTS,
)
from .faker_instance import fake
from .helpers import (
    generate_initials,
    generate_personal_id,
    generate_policy_number,
    generate_registration_date,
    introduce_name_noise,
    random_birthdate,
)

PATIENT_COLUMNS = [
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

SOURCE_TABLE_MAP = {
    "EPD_A": "epd_a",
    "EPD_B": "epd_b",
    "EPD_C": "epd_c",
}


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
    if not base_number:
        base_number = "1"
    try:
        if int(base_number) <= 0:
            base_number = "1"
    except ValueError:
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


def _mutate_postal_code(postal_code: str) -> str:
    if not postal_code:
        return postal_code

    r = random.random()
    compact = postal_code.replace(" ", "")
    if r < 0.4:
        return compact
    if r < 0.7 and len(compact) >= 6:
        return f"{compact[:4]} {compact[4:]}".lower()
    if r < 0.9:
        return postal_code.lower()
    return postal_code


def _mutate_house_number_fields(house_number: str, house_number_addition: str | None) -> tuple[str, str | None]:
    number, addition = split_house_number(house_number)
    effective_addition = house_number_addition or addition

    if not effective_addition:
        if random.random() < 0.5:
            return f"{number}{random.choice(['A', 'B', 'C'])}", None
        return number, None

    entry_type = random.choices(
        ["correct", "forgot_to_split", "double_entry"],
        weights=[0.78, 0.14, 0.08],
    )[0]

    if entry_type == "correct":
        return number, effective_addition
    if entry_type == "forgot_to_split":
        return f"{number}{effective_addition}", None
    return f"{number}{effective_addition}", effective_addition


def _build_master_patients(gps_df: pd.DataFrame, ins_df: pd.DataFrame, n: int) -> pd.DataFrame:
    patients: list[dict[str, object]] = []

    gp_codes = gps_df["gp_code"].tolist()
    insurance_codes = ins_df["insurance_code"].tolist()
    gp_weights = np.random.dirichlet(np.ones(len(gp_codes)))
    insurance_weights = np.random.dirichlet(np.ones(len(insurance_codes)))

    for index in range(n):
        house_number, house_number_addition = generate_house_number_with_noise()
        first_name = fake.first_name()

        patients.append(
            {
                "golden_patient_id": f"G{index + 1:07d}",
                "first_name": first_name,
                "last_name": fake.last_name(),
                "middle_name": random.choice(["", "", "van", "de", "van der"]),
                "initials": generate_initials(first_name),
                "gender": random.choice(["M", "V"]),
                "birth_date": random_birthdate(),
                "registration_date": None,
                "email": fake.email(),
                "phone": fake.phone_number(),
                "street": fake.street_name(),
                "house_number": house_number,
                "house_number_addition": house_number_addition,
                "postal_code": fake.postcode(),
                "city": fake.city(),
                "gp_code": random.choices(gp_codes, weights=gp_weights)[0],
                "insurance_code": random.choices(insurance_codes, weights=insurance_weights)[0],
                "policy_number": generate_policy_number(),
                "personal_identification_number": generate_personal_id(),
            }
        )

    master_df = pd.DataFrame(patients)
    master_df["registration_date"] = master_df["birth_date"].apply(generate_registration_date)
    return master_df


def _choose_source_count() -> int:
    counts = list(SOURCE_OVERLAP_DISTRIBUTION.keys())
    probabilities = list(SOURCE_OVERLAP_DISTRIBUTION.values())
    return random.choices(counts, weights=probabilities, k=1)[0]


def _choose_sources_for_patient() -> list[str]:
    count = _choose_source_count()

    if count == 1:
        return [
            random.choices(
                list(SOURCE_VOLUME_WEIGHTS.keys()),
                weights=list(SOURCE_VOLUME_WEIGHTS.values()),
                k=1,
            )[0]
        ]

    if count == 2:
        selected_pair = random.choices(
            list(SOURCE_PAIR_WEIGHTS.keys()),
            weights=list(SOURCE_PAIR_WEIGHTS.values()),
            k=1,
        )[0]
        return list(selected_pair)

    return list(SOURCE_SYSTEMS)


def _apply_source_noise(record: dict[str, object], source_system: str, is_cross_copy: bool) -> dict[str, object]:
    noisy = dict(record)
    profile = SOURCE_NOISE_PROFILES[source_system]

    if random.random() < profile["name_noise_rate"]:
        noisy["first_name"] = introduce_name_noise(str(noisy["first_name"]))
    if random.random() < profile["name_noise_rate"]:
        noisy["last_name"] = introduce_name_noise(str(noisy["last_name"]))

    noisy["initials"] = generate_initials(str(noisy["first_name"]))

    if random.random() < profile["email_missing_rate"]:
        noisy["email"] = None
    if random.random() < profile["phone_missing_rate"]:
        noisy["phone"] = None

    if random.random() < profile["address_noise_rate"]:
        house_number, house_number_addition = _mutate_house_number_fields(
            str(noisy["house_number"]),
            noisy["house_number_addition"],
        )
        noisy["house_number"] = house_number
        noisy["house_number_addition"] = house_number_addition

    if random.random() < profile["postal_code_noise_rate"]:
        noisy["postal_code"] = _mutate_postal_code(str(noisy["postal_code"]))

    if random.random() < profile["pin_corruption_rate"]:
        noisy["personal_identification_number"] = generate_personal_id()

    if is_cross_copy:
        if random.random() < profile["cross_registration_shift_prob"]:
            max_days = int(profile["cross_registration_shift_max_days"])
            registration_date = noisy["registration_date"]
            noisy["registration_date"] = registration_date + timedelta(
                days=random.randint(-max_days, max_days)
            )

        if random.random() < CROSS_SOURCE_VARIANT_RATES[source_system]:
            variant_type = random.choice(["email", "street", "house"])
            if variant_type == "email":
                noisy["email"] = None
            elif variant_type == "street":
                noisy["street"] = fake.street_name()
                noisy["postal_code"] = fake.postcode()
                noisy["city"] = fake.city()
            else:
                house_number, house_number_addition = _mutate_house_number_fields(
                    str(noisy["house_number"]),
                    noisy["house_number_addition"],
                )
                noisy["house_number"] = house_number
                noisy["house_number_addition"] = house_number_addition

    return noisy


def _create_near_duplicate(record: dict[str, object]) -> dict[str, object]:
    near_dup = dict(record)
    near_dup["original_patient_id"] = None
    near_dup["birth_date"] = near_dup["birth_date"] + timedelta(days=random.randint(-300, 300))
    near_dup["registration_date"] = generate_registration_date(near_dup["birth_date"])
    near_dup["personal_identification_number"] = generate_personal_id()
    near_dup["policy_number"] = generate_policy_number()

    # Keep near-duplicates plausible by changing only a small set of fields.
    if random.random() < 0.65:
        near_dup["first_name"] = introduce_name_noise(str(near_dup["first_name"]))
    if random.random() < 0.65:
        near_dup["last_name"] = introduce_name_noise(str(near_dup["last_name"]))
    near_dup["initials"] = generate_initials(str(near_dup["first_name"]))

    return near_dup


def _create_source_patient_rows(master_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows_by_source: dict[str, list[dict[str, object]]] = {source: [] for source in SOURCE_SYSTEMS}
    source_counters = {source: 0 for source in SOURCE_SYSTEMS}

    for _, master_row in master_df.iterrows():
        selected_sources = _choose_sources_for_patient()
        base_record = master_row.to_dict()

        anchor_patient_id = None
        for source_system in selected_sources:
            source_counters[source_system] += 1
            patient_id = f"{source_system[-1]}P{source_counters[source_system]:07d}"

            source_record = _apply_source_noise(
                base_record,
                source_system,
                is_cross_copy=anchor_patient_id is not None,
            )
            source_record["patient_id"] = patient_id
            source_record["source_system"] = source_system

            if anchor_patient_id is None:
                source_record["original_patient_id"] = None
                anchor_patient_id = patient_id
            else:
                source_record["original_patient_id"] = anchor_patient_id

            source_record.pop("golden_patient_id", None)
            rows_by_source[source_system].append(source_record)

    source_frames: dict[str, pd.DataFrame] = {}
    for source_system in SOURCE_SYSTEMS:
        source_frames[source_system] = pd.DataFrame(rows_by_source[source_system])[PATIENT_COLUMNS]

    return source_frames


def _inject_intra_source_duplicates(source_frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    for source_system in SOURCE_SYSTEMS:
        source_df = source_frames[source_system]
        source_count = len(source_df)
        dup_count = int(source_count * INTRA_SOURCE_DUP_RATES[source_system])
        if dup_count <= 0:
            continue

        indices = np.random.choice(source_count, size=dup_count, replace=False)
        duplicate_rows: list[dict[str, object]] = []

        next_counter = source_count
        for idx in indices:
            base_record = source_df.iloc[idx].to_dict()
            next_counter += 1

            duplicate_record = _apply_source_noise(base_record, source_system, is_cross_copy=True)
            duplicate_record["patient_id"] = f"{source_system[-1]}P{next_counter:07d}"
            duplicate_record["source_system"] = source_system
            duplicate_record["original_patient_id"] = base_record["patient_id"]
            duplicate_rows.append(duplicate_record)

        source_frames[source_system] = pd.concat(
            [source_df, pd.DataFrame(duplicate_rows)[PATIENT_COLUMNS]],
            ignore_index=True,
        )

    return source_frames


def _inject_false_positives(source_frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    for source_system in SOURCE_SYSTEMS:
        source_df = source_frames[source_system]
        source_count = len(source_df)
        false_positive_count = int(source_count * FALSE_POSITIVE_RATES[source_system])
        if false_positive_count <= 0:
            continue

        indices = np.random.choice(source_count, size=false_positive_count, replace=False)
        false_positive_rows: list[dict[str, object]] = []

        next_counter = source_count
        for idx in indices:
            base_record = source_df.iloc[idx].to_dict()
            next_counter += 1

            false_positive_record = _create_near_duplicate(base_record)
            false_positive_record["patient_id"] = f"{source_system[-1]}P{next_counter:07d}"
            false_positive_record["source_system"] = source_system
            false_positive_rows.append(false_positive_record)

        source_frames[source_system] = pd.concat(
            [source_df, pd.DataFrame(false_positive_rows)[PATIENT_COLUMNS]],
            ignore_index=True,
        )

    return source_frames


def generate_patients_by_source(
    gps_df: pd.DataFrame,
    ins_df: pd.DataFrame,
    n: int = N_PATIENTS,
) -> dict[str, pd.DataFrame]:
    master_df = _build_master_patients(gps_df, ins_df, n)
    source_frames = _create_source_patient_rows(master_df)
    source_frames = _inject_intra_source_duplicates(source_frames)
    source_frames = _inject_false_positives(source_frames)
    return source_frames


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
            cur.execute("CREATE SCHEMA IF NOT EXISTS src")

            for source_system, table_name in SOURCE_TABLE_MAP.items():
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS src.{table_name} (
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

                    ALTER TABLE src.{table_name}
                    ADD COLUMN IF NOT EXISTS house_number_addition TEXT
                    """
                )

                source_df = df[df["source_system"] == source_system]
                if source_df.empty:
                    continue

                rows = list(source_df[PATIENT_COLUMNS].itertuples(index=False, name=None))
                cur.executemany(
                    f"""
                    INSERT INTO src.{table_name} (
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
    source_frames = generate_patients_by_source(gps_df, ins_df, n=n)
    result = pd.concat([source_frames[source] for source in SOURCE_SYSTEMS], ignore_index=True)

    if insert_to_postgres:
        insert_patients_to_postgres(result)

    return result