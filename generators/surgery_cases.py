import random
from datetime import datetime, timedelta

import pandas as pd

from .config import N_SURGERY_CASES
from .providers import ANESTHESIOLOGISTS, SURGEONS

SURGERY_CASE_COLUMNS = [
    "surgerycaseid",
    "patientid",
    "encounterid",
    "patientname",
    "dateofbirth",
    "primarysurgeon_code",
    "primarysurgeon",
    "assistantsurgeon_code",
    "assistantsurgeon",
    "anesthesiologist_code",
    "anesthesiologist",
    "specialty",
    "procedurecode",
    "proceduredescription",
    "diagnosiscode",
    "diagnosisdescription",
    "operatingroom",
    "urgency",
    "anesthesiatype",
    "scheduledstart_ts",
    "patientinroom_ts",
    "procedure_start",
    "procedureend",
    "patientoutroom",
    "complication_flag",
    "complication_description",
    "payer_code",
    "estimated_cost",
    "procedure_status",
    "cancellationreason",
]

SPECIALTY_CATALOG: dict[str, dict[str, object]] = {
    "General Surgery": {
        "procedures": [
            ("GS1001", "Laparoscopic appendectomy", 4200),
            ("GS1002", "Laparoscopic cholecystectomy", 6800),
            ("GS1003", "Inguinal hernia repair", 4600),
        ],
        "diagnoses": [
            ("K35.80", "Acute appendicitis"),
            ("K80.20", "Cholelithiasis without cholecystitis"),
            ("K40.90", "Unilateral inguinal hernia"),
        ],
        "duration_minutes": (45, 170),
    },
    "Orthopedics": {
        "procedures": [
            ("OR2001", "Total hip arthroplasty", 16500),
            ("OR2002", "Knee arthroscopy", 9300),
            ("OR2003", "Open reduction internal fixation femur", 14800),
        ],
        "diagnoses": [
            ("M16.11", "Unilateral primary osteoarthritis of hip"),
            ("S72.90", "Femur fracture, unspecified"),
            ("M23.91", "Derangement of knee, unspecified"),
        ],
        "duration_minutes": (60, 210),
    },
    "Cardiothoracic": {
        "procedures": [
            ("CT3001", "Coronary artery bypass graft", 42000),
            ("CT3002", "Aortic valve replacement", 39000),
            ("CT3003", "Lobectomy", 27500),
        ],
        "diagnoses": [
            ("I25.10", "Atherosclerotic heart disease"),
            ("I35.0", "Aortic valve stenosis"),
            ("C34.90", "Malignant neoplasm of bronchus or lung"),
        ],
        "duration_minutes": (140, 360),
    },
    "Neurosurgery": {
        "procedures": [
            ("NS4001", "Lumbar laminectomy", 13800),
            ("NS4002", "Craniotomy for tumor resection", 45500),
            ("NS4003", "VP shunt placement", 11200),
        ],
        "diagnoses": [
            ("M48.06", "Spinal stenosis, lumbar region"),
            ("D33.2", "Benign neoplasm of brain"),
            ("G91.9", "Hydrocephalus, unspecified"),
        ],
        "duration_minutes": (90, 340),
    },
    "Gynecology": {
        "procedures": [
            ("GY5001", "Total abdominal hysterectomy", 12500),
            ("GY5002", "Diagnostic hysteroscopy", 5100),
            ("GY5003", "Ovarian cystectomy", 9200),
        ],
        "diagnoses": [
            ("D25.9", "Leiomyoma of uterus"),
            ("N84.0", "Polyp of corpus uteri"),
            ("N83.20", "Unspecified ovarian cyst"),
        ],
        "duration_minutes": (40, 200),
    },
}

ANESTHESIA_BY_SPECIALTY: dict[str, list[tuple[str, int]]] = {
    "General Surgery": [("General", 72), ("Regional", 14), ("MAC", 14)],
    "Orthopedics": [("General", 46), ("Spinal", 39), ("Regional", 15)],
    "Cardiothoracic": [("General", 96), ("Regional", 2), ("MAC", 2)],
    "Neurosurgery": [("General", 93), ("Regional", 4), ("MAC", 3)],
    "Gynecology": [("General", 70), ("Regional", 18), ("MAC", 12)],
}

SPECIALTY_WEIGHTS = {
    "General Surgery": 0.34,
    "Orthopedics": 0.27,
    "Cardiothoracic": 0.11,
    "Neurosurgery": 0.09,
    "Gynecology": 0.19,
}

PAYER_MIX = {
    "CZ": 0.21,
    "VGZ": 0.19,
    "ZK": 0.17,
    "MEN": 0.14,
    "DSW": 0.08,
    "NN": 0.08,
    "ONVZ": 0.07,
    "ASR": 0.06,
}

OPERATING_ROOMS = [f"OR-{idx:02d}" for idx in range(1, 13)]

URGENCY_WEIGHTS = {
    "Elective": 0.72,
    "Urgent": 0.22,
    "Emergency": 0.06,
}

STATUS_WEIGHTS = {
    "Completed": 0.86,
    "Cancelled": 0.08,
    "In Progress": 0.04,
    "Scheduled": 0.02,
}

COMPLICATION_OPTIONS = [
    "Postoperative bleeding",
    "Difficult airway",
    "Hemodynamic instability",
    "Intraoperative arrhythmia",
    "Surgical site issue requiring revision",
]

CANCELLATION_REASONS = [
    "No OR capacity",
    "Patient not fit for surgery",
    "Missing pre-op lab result",
    "Equipment unavailable",
    "Patient no-show",
]

CASES_PER_PATIENT_DISTRIBUTION = {
    1: 0.68,
    2: 0.21,
    3: 0.07,
    4: 0.03,
    5: 0.01,
}


def _draw_from_weighted_map(weighted_map: dict[str, float]) -> str:
    keys = list(weighted_map.keys())
    weights = list(weighted_map.values())
    return random.choices(keys, weights=weights, k=1)[0]


def _draw_cases_for_patient() -> int:
    counts = list(CASES_PER_PATIENT_DISTRIBUTION.keys())
    weights = list(CASES_PER_PATIENT_DISTRIBUTION.values())
    return random.choices(counts, weights=weights, k=1)[0]


def _build_patient_case_plan(
    patient_records: list[dict[str, object]],
    n_cases: int,
) -> list[tuple[dict[str, object], int]]:
    if not patient_records or n_cases <= 0:
        return []

    shuffled_patients = patient_records[:]
    random.shuffle(shuffled_patients)

    plan: list[tuple[dict[str, object], int]] = []
    total_cases = 0
    patient_index = 0

    while total_cases < n_cases and patient_index < len(shuffled_patients):
        case_count = _draw_cases_for_patient()
        remaining = n_cases - total_cases
        case_count = min(case_count, remaining)

        plan.append((shuffled_patients[patient_index], case_count))
        total_cases += case_count
        patient_index += 1

    # Fallback for very high n_cases relative to available patients.
    while total_cases < n_cases and plan:
        weights = [1.0 / (assigned_cases + 0.75) for _, assigned_cases in plan]
        selected_idx = random.choices(range(len(plan)), weights=weights, k=1)[0]
        selected_patient, assigned_cases = plan[selected_idx]
        plan[selected_idx] = (selected_patient, assigned_cases + 1)
        total_cases += 1

    return plan


def _pick_anesthesia(specialty: str) -> str:
    choices = ANESTHESIA_BY_SPECIALTY[specialty]
    values = [item[0] for item in choices]
    weights = [item[1] for item in choices]
    return random.choices(values, weights=weights, k=1)[0]


def _format_clinician_name(first_name: str, last_name: str) -> str:
    format_type = random.choices(
        ["full", "initial_last_spaced", "initial_last_compact", "last_only"],
        weights=[0.62, 0.18, 0.12, 0.08],
        k=1,
    )[0]

    if format_type == "full":
        return f"{first_name} {last_name}"

    if format_type == "initial_last_spaced":
        return f"{first_name[0]}. {last_name}"

    if format_type == "initial_last_compact":
        return f"{first_name[0]}.{last_name}"

    return last_name


def _surgeons_for_specialty(specialty: str) -> list[dict[str, str]]:
    return [clinician for clinician in SURGEONS if clinician["specialty"] == specialty]


def _scheduled_start_window(urgency: str) -> datetime:
    now = datetime.now()
    if urgency == "Emergency":
        start = now - timedelta(days=90)
        return start + timedelta(minutes=random.randint(0, 90 * 24 * 60))

    if urgency == "Urgent":
        start = now - timedelta(days=240)
        return start + timedelta(minutes=random.randint(0, 240 * 24 * 60))

    start = now - timedelta(days=365)
    return start + timedelta(minutes=random.randint(0, 365 * 24 * 60))


def _build_case_timestamps(
    status: str,
    urgency: str,
    duration_range: tuple[int, int],
) -> tuple[datetime, datetime | None, datetime | None, datetime | None, datetime | None]:
    scheduled = _scheduled_start_window(urgency).replace(second=0, microsecond=0)

    if status == "Cancelled":
        return scheduled, None, None, None, None

    if status == "Scheduled":
        if scheduled < datetime.now() + timedelta(hours=6):
            scheduled = datetime.now().replace(second=0, microsecond=0) + timedelta(
                hours=random.randint(6, 21)
            )
        return scheduled, None, None, None, None

    in_room_lag = random.randint(-20, 50)
    patient_in_room = scheduled + timedelta(minutes=in_room_lag)
    procedure_start = patient_in_room + timedelta(minutes=random.randint(8, 28))

    base_duration = random.randint(duration_range[0], duration_range[1])
    if urgency == "Emergency":
        base_duration = max(duration_range[0], int(base_duration * 0.9))

    if status == "In Progress":
        elapsed = random.randint(20, max(30, base_duration - 5))
        procedure_end = None
        patient_out_room = None
        return (
            scheduled,
            patient_in_room,
            procedure_start,
            procedure_start + timedelta(minutes=elapsed),
            patient_out_room,
        )

    procedure_end = procedure_start + timedelta(minutes=base_duration)
    patient_out_room = procedure_end + timedelta(minutes=random.randint(10, 40))
    return scheduled, patient_in_room, procedure_start, procedure_end, patient_out_room


def _format_ts(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")


def generate_surgery_cases(
    patients_df: pd.DataFrame,
    n: int = N_SURGERY_CASES,
) -> pd.DataFrame:
    if patients_df.empty:
        return pd.DataFrame(columns=SURGERY_CASE_COLUMNS)

    if "patient_id" not in patients_df.columns:
        raise ValueError("patients_df must include patient_id")

    if "insurance_code" not in patients_df.columns:
        raise ValueError("patients_df must include insurance_code")

    cases: list[dict[str, object]] = []

    patient_rows = patients_df[
        ["patient_id", "first_name", "middle_name", "last_name", "birth_date", "insurance_code"]
    ].drop_duplicates(subset=["patient_id"])

    patient_records = patient_rows.to_dict(orient="records")
    patient_case_plan = _build_patient_case_plan(patient_records, n)

    case_index = 0
    for patient, assigned_case_count in patient_case_plan:
        for _ in range(assigned_case_count):
            case_index += 1

            specialty = _draw_from_weighted_map(SPECIALTY_WEIGHTS)
            specialty_data = SPECIALTY_CATALOG[specialty]

            procedure_code, procedure_description, base_cost = random.choice(
                specialty_data["procedures"]
            )
            diagnosis_code, diagnosis_description = random.choice(specialty_data["diagnoses"])

            urgency = _draw_from_weighted_map(URGENCY_WEIGHTS)
            status = _draw_from_weighted_map(STATUS_WEIGHTS)

            (
                scheduled,
                patient_in_room,
                procedure_start,
                procedure_end,
                patient_out_room,
            ) = _build_case_timestamps(
                status,
                urgency,
                specialty_data["duration_minutes"],
            )

            specialty_surgeons = _surgeons_for_specialty(specialty)
            primary_surgeon = random.choice(specialty_surgeons)
            assistant_surgeon = random.choice(
                [clinician for clinician in specialty_surgeons if clinician["code"] != primary_surgeon["code"]]
            )
            anesthesiologist = random.choice(ANESTHESIOLOGISTS)

            anesthesia_type = _pick_anesthesia(specialty)

            complication_flag = "N"
            complication_description = None
            if status == "Completed":
                complication_probability = 0.055 if urgency != "Emergency" else 0.12
                if random.random() < complication_probability:
                    complication_flag = "Y"
                    complication_description = random.choice(COMPLICATION_OPTIONS)

            cancellation_reason = None
            if status == "Cancelled":
                cancellation_reason = random.choice(CANCELLATION_REASONS)

            payer_code = patient["insurance_code"]
            if random.random() < 0.06:
                payer_code = _draw_from_weighted_map(PAYER_MIX)

            cost_multiplier = random.uniform(0.88, 1.42)
            if urgency == "Emergency":
                cost_multiplier *= random.uniform(1.05, 1.25)
            if complication_flag == "Y":
                cost_multiplier *= random.uniform(1.08, 1.3)
            if status == "Cancelled":
                estimated_cost = round(base_cost * random.uniform(0.03, 0.2), 2)
            else:
                estimated_cost = round(base_cost * cost_multiplier, 2)

            middle_name = (patient.get("middle_name") or "").strip()
            full_name = f"{patient['first_name']} {middle_name} {patient['last_name']}".replace("  ", " ").strip()

            cases.append(
                {
                    "surgerycaseid": f"SC{case_index:08d}",
                    "patientid": patient["patient_id"],
                    "encounterid": f"ENC{case_index:08d}",
                    "patientname": full_name,
                    "dateofbirth": patient["birth_date"],
                    "primarysurgeon_code": primary_surgeon["code"],
                    "primarysurgeon": _format_clinician_name(
                        primary_surgeon["first_name"],
                        primary_surgeon["last_name"],
                    ),
                    "assistantsurgeon_code": assistant_surgeon["code"],
                    "assistantsurgeon": _format_clinician_name(
                        assistant_surgeon["first_name"],
                        assistant_surgeon["last_name"],
                    ),
                    "anesthesiologist_code": anesthesiologist["code"],
                    "anesthesiologist": _format_clinician_name(
                        anesthesiologist["first_name"],
                        anesthesiologist["last_name"],
                    ),
                    "specialty": specialty,
                    "procedurecode": procedure_code,
                    "proceduredescription": procedure_description,
                    "diagnosiscode": diagnosis_code,
                    "diagnosisdescription": diagnosis_description,
                    "operatingroom": random.choice(OPERATING_ROOMS),
                    "urgency": urgency,
                    "anesthesiatype": anesthesia_type,
                    "scheduledstart_ts": _format_ts(scheduled),
                    "patientinroom_ts": _format_ts(patient_in_room),
                    "procedure_start": _format_ts(procedure_start),
                    "procedureend": _format_ts(procedure_end),
                    "patientoutroom": _format_ts(patient_out_room),
                    "complication_flag": complication_flag,
                    "complication_description": complication_description,
                    "payer_code": payer_code,
                    "estimated_cost": estimated_cost,
                    "procedure_status": status,
                    "cancellationreason": cancellation_reason,
                }
            )

    return pd.DataFrame(cases, columns=SURGERY_CASE_COLUMNS)
