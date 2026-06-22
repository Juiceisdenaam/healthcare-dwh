import random

import numpy as np
import pandas as pd

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


def generate_patients(gps_df: pd.DataFrame, ins_df: pd.DataFrame, n: int = N_PATIENTS) -> pd.DataFrame:
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
                "house_number": fake.building_number(),
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

    return pd.concat([df, cross_dups, same_dups, partial_dups, false_pos], ignore_index=True)