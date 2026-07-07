import random
from datetime import datetime, timedelta

import pandas as pd

from .config import N_ENCOUNTERS
from .providers import ATTENDING_PHYSICIANS

ENCOUNTER_COLUMNS = [
    "encounterid",
    "patientid",
    "encounter_type",
    "encounter_status",
    "admit_ts",
    "discharge_ts",
    "department_code",
    "department_name",
    "attending_provider_code",
    "attending_provider_name",
    "facility_code",
    "facility_name",
    "primary_diagnosis_code",
    "primary_diagnosis_description",
    "payer_code",
    "related_surgerycaseid",
]

FACILITIES = [
    ("HOSP01", "St. Antonius Hospital"),
    ("HOSP02", "Riverbank Medical Center"),
]

NON_SURGICAL_ENCOUNTER_TYPES = {
    "Outpatient": 0.48,
    "Emergency": 0.18,
    "Inpatient": 0.17,
    "Daycase": 0.12,
    "Observation": 0.05,
}

NON_SURGICAL_DIAGNOSES = [
    ("R07.9", "Chest pain, unspecified", "DEP_CARD", "Cardiology"),
    ("J18.9", "Pneumonia, unspecified organism", "DEP_PULM", "Pulmonology"),
    ("G45.9", "Transient cerebral ischemic attack", "DEP_NEURO", "Neurology"),
    ("R55", "Syncope and collapse", "DEP_ED", "Emergency Department"),
    ("N39.0", "Urinary tract infection", "DEP_IM", "Internal Medicine"),
    ("R53.1", "Weakness", "DEP_GER", "Geriatrics"),
]

SURGERY_DEPARTMENT_MAP = {
    "General Surgery": ("DEP_GENSURG", "General Surgery"),
    "Orthopedics": ("DEP_ORTHO", "Orthopedics"),
    "Cardiothoracic": ("DEP_CARDSURG", "Cardiothoracic Surgery"),
    "Neurosurgery": ("DEP_NEUROSURG", "Neurosurgery"),
    "Gynecology": ("DEP_GYN", "Gynecology"),
}


def _format_ts(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _draw_weighted(weighted_map: dict[str, float]) -> str:
    keys = list(weighted_map.keys())
    weights = list(weighted_map.values())
    return random.choices(keys, weights=weights, k=1)[0]


def _non_surgical_timestamps(encounter_type: str) -> tuple[datetime, datetime | None]:
    admit_ts = datetime.now() - timedelta(days=random.randint(1, 365), minutes=random.randint(0, 1440))

    if encounter_type == "Outpatient":
        discharge_ts = admit_ts + timedelta(minutes=random.randint(20, 90))
    elif encounter_type == "Emergency":
        discharge_ts = admit_ts + timedelta(hours=random.randint(2, 14))
    elif encounter_type == "Observation":
        discharge_ts = admit_ts + timedelta(hours=random.randint(8, 36))
    elif encounter_type == "Daycase":
        discharge_ts = admit_ts + timedelta(hours=random.randint(4, 10))
    else:
        discharge_ts = admit_ts + timedelta(days=random.randint(1, 9), hours=random.randint(0, 12))

    return admit_ts.replace(second=0, microsecond=0), discharge_ts.replace(second=0, microsecond=0)


def _surgery_encounter_row(surgery_row: pd.Series) -> dict[str, object]:
    department_code, department_name = SURGERY_DEPARTMENT_MAP[surgery_row["specialty"]]
    facility_code, facility_name = random.choice(FACILITIES)

    scheduled_ts = pd.to_datetime(surgery_row["scheduledstart_ts"]) if surgery_row["scheduledstart_ts"] else None
    patient_out_room = pd.to_datetime(surgery_row["patientoutroom"]) if surgery_row["patientoutroom"] else None

    if surgery_row["procedure_status"] == "Cancelled":
        admit_ts = scheduled_ts - timedelta(hours=random.randint(6, 48)) if scheduled_ts is not None else None
        discharge_ts = None
        encounter_status = "Cancelled"
    elif surgery_row["procedure_status"] == "Scheduled":
        admit_ts = scheduled_ts - timedelta(hours=random.randint(6, 24)) if scheduled_ts is not None else None
        discharge_ts = None
        encounter_status = "Scheduled"
    elif surgery_row["procedure_status"] == "In Progress":
        admit_ts = scheduled_ts - timedelta(hours=random.randint(4, 24)) if scheduled_ts is not None else None
        discharge_ts = None
        encounter_status = "In Progress"
    else:
        admit_ts = scheduled_ts - timedelta(hours=random.randint(4, 30)) if scheduled_ts is not None else None
        discharge_ts = patient_out_room + timedelta(hours=random.randint(6, 72)) if patient_out_room is not None else None
        encounter_status = "Discharged"

    encounter_type = "Day Surgery"
    if surgery_row["urgency"] == "Emergency":
        encounter_type = "Emergency Surgery"
    elif surgery_row["specialty"] in {"Cardiothoracic", "Neurosurgery"}:
        encounter_type = "Inpatient Surgery"

    return {
        "encounterid": surgery_row["encounterid"],
        "patientid": surgery_row["patientid"],
        "encounter_type": encounter_type,
        "encounter_status": encounter_status,
        "admit_ts": _format_ts(admit_ts.to_pydatetime() if admit_ts is not None else None),
        "discharge_ts": _format_ts(discharge_ts.to_pydatetime() if discharge_ts is not None else None),
        "department_code": department_code,
        "department_name": department_name,
        "attending_provider_code": surgery_row["primarysurgeon_code"],
        "attending_provider_name": surgery_row["primarysurgeon"],
        "facility_code": facility_code,
        "facility_name": facility_name,
        "primary_diagnosis_code": surgery_row["diagnosiscode"],
        "primary_diagnosis_description": surgery_row["diagnosisdescription"],
        "payer_code": surgery_row["payer_code"],
        "related_surgerycaseid": surgery_row["surgerycaseid"],
    }


def _non_surgical_encounter_row(patient: dict[str, object], encounter_index: int) -> dict[str, object]:
    encounter_type = _draw_weighted(NON_SURGICAL_ENCOUNTER_TYPES)
    diagnosis_code, diagnosis_description, department_code, department_name = random.choice(
        NON_SURGICAL_DIAGNOSES
    )
    provider = random.choice(ATTENDING_PHYSICIANS)
    facility_code, facility_name = random.choice(FACILITIES)
    admit_ts, discharge_ts = _non_surgical_timestamps(encounter_type)

    return {
        "encounterid": f"ENC{encounter_index:08d}",
        "patientid": patient["patient_id"],
        "encounter_type": encounter_type,
        "encounter_status": "Discharged",
        "admit_ts": _format_ts(admit_ts),
        "discharge_ts": _format_ts(discharge_ts),
        "department_code": department_code,
        "department_name": department_name,
        "attending_provider_code": provider["code"],
        "attending_provider_name": f"{provider['first_name']} {provider['last_name']}",
        "facility_code": facility_code,
        "facility_name": facility_name,
        "primary_diagnosis_code": diagnosis_code,
        "primary_diagnosis_description": diagnosis_description,
        "payer_code": patient["insurance_code"],
        "related_surgerycaseid": None,
    }


def generate_encounters(
    patients_df: pd.DataFrame,
    surgery_cases_df: pd.DataFrame,
    n: int = N_ENCOUNTERS,
) -> pd.DataFrame:
    encounters: list[dict[str, object]] = []

    if not surgery_cases_df.empty:
        encounters.extend(_surgery_encounter_row(row) for _, row in surgery_cases_df.iterrows())

    additional_needed = max(n - len(encounters), 0)
    if additional_needed > 0 and not patients_df.empty:
        patient_rows = patients_df[["patient_id", "insurance_code"]].drop_duplicates(subset=["patient_id"])
        patient_records = patient_rows.to_dict(orient="records")
        starting_index = len(encounters)

        for offset in range(additional_needed):
            patient = random.choice(patient_records)
            encounter_index = starting_index + offset + 1
            encounters.append(_non_surgical_encounter_row(patient, encounter_index))

    return pd.DataFrame(encounters, columns=ENCOUNTER_COLUMNS)