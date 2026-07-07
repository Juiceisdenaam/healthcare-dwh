import pandas as pd

SURGEONS = [
    {
        "code": "SURG001",
        "first_name": "Jan",
        "last_name": "Jansen",
        "provider_type": "Surgeon",
        "specialty": "General Surgery",
        "department_code": "DEP_GENSURG",
        "department_name": "General Surgery",
    },
    {
        "code": "SURG002",
        "first_name": "Anne",
        "last_name": "van Dijk",
        "provider_type": "Surgeon",
        "specialty": "General Surgery",
        "department_code": "DEP_GENSURG",
        "department_name": "General Surgery",
    },
    {
        "code": "SURG003",
        "first_name": "Lars",
        "last_name": "de Vries",
        "provider_type": "Surgeon",
        "specialty": "Orthopedics",
        "department_code": "DEP_ORTHO",
        "department_name": "Orthopedics",
    },
    {
        "code": "SURG004",
        "first_name": "Pieter",
        "last_name": "Bakker",
        "provider_type": "Surgeon",
        "specialty": "Orthopedics",
        "department_code": "DEP_ORTHO",
        "department_name": "Orthopedics",
    },
    {
        "code": "SURG005",
        "first_name": "Sanne",
        "last_name": "Smit",
        "provider_type": "Surgeon",
        "specialty": "Cardiothoracic",
        "department_code": "DEP_CARDSURG",
        "department_name": "Cardiothoracic Surgery",
    },
    {
        "code": "SURG006",
        "first_name": "Koen",
        "last_name": "Visser",
        "provider_type": "Surgeon",
        "specialty": "Cardiothoracic",
        "department_code": "DEP_CARDSURG",
        "department_name": "Cardiothoracic Surgery",
    },
    {
        "code": "SURG007",
        "first_name": "Thomas",
        "last_name": "Bos",
        "provider_type": "Surgeon",
        "specialty": "Neurosurgery",
        "department_code": "DEP_NEUROSURG",
        "department_name": "Neurosurgery",
    },
    {
        "code": "SURG008",
        "first_name": "Ruben",
        "last_name": "Mulder",
        "provider_type": "Surgeon",
        "specialty": "Neurosurgery",
        "department_code": "DEP_NEUROSURG",
        "department_name": "Neurosurgery",
    },
    {
        "code": "SURG009",
        "first_name": "Nina",
        "last_name": "Peters",
        "provider_type": "Surgeon",
        "specialty": "Gynecology",
        "department_code": "DEP_GYN",
        "department_name": "Gynecology",
    },
    {
        "code": "SURG010",
        "first_name": "Joris",
        "last_name": "Kuiper",
        "provider_type": "Surgeon",
        "specialty": "Gynecology",
        "department_code": "DEP_GYN",
        "department_name": "Gynecology",
    },
]

ANESTHESIOLOGISTS = [
    {
        "code": "ANES001",
        "first_name": "Femke",
        "last_name": "Meijer",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
    {
        "code": "ANES002",
        "first_name": "Hugo",
        "last_name": "Vos",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
    {
        "code": "ANES003",
        "first_name": "Cas",
        "last_name": "Groen",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
    {
        "code": "ANES004",
        "first_name": "Yara",
        "last_name": "Willems",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
    {
        "code": "ANES005",
        "first_name": "Daan",
        "last_name": "Kok",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
    {
        "code": "ANES006",
        "first_name": "Gijs",
        "last_name": "de Boer",
        "provider_type": "Anesthesiologist",
        "specialty": "Anesthesiology",
        "department_code": "DEP_ANES",
        "department_name": "Anesthesiology",
    },
]

ATTENDING_PHYSICIANS = [
    {
        "code": "PHYS001",
        "first_name": "Eva",
        "last_name": "van Leeuwen",
        "provider_type": "Hospitalist",
        "specialty": "Internal Medicine",
        "department_code": "DEP_IM",
        "department_name": "Internal Medicine",
    },
    {
        "code": "PHYS002",
        "first_name": "Mark",
        "last_name": "Vermeer",
        "provider_type": "Hospitalist",
        "specialty": "Cardiology",
        "department_code": "DEP_CARD",
        "department_name": "Cardiology",
    },
    {
        "code": "PHYS003",
        "first_name": "Lotte",
        "last_name": "de Jong",
        "provider_type": "Emergency Physician",
        "specialty": "Emergency Medicine",
        "department_code": "DEP_ED",
        "department_name": "Emergency Department",
    },
    {
        "code": "PHYS004",
        "first_name": "Ahmed",
        "last_name": "El Mansouri",
        "provider_type": "Neurologist",
        "specialty": "Neurology",
        "department_code": "DEP_NEURO",
        "department_name": "Neurology",
    },
    {
        "code": "PHYS005",
        "first_name": "Sophie",
        "last_name": "Blom",
        "provider_type": "Pulmonologist",
        "specialty": "Pulmonology",
        "department_code": "DEP_PULM",
        "department_name": "Pulmonology",
    },
    {
        "code": "PHYS006",
        "first_name": "Tom",
        "last_name": "van den Berg",
        "provider_type": "Internist",
        "specialty": "Geriatrics",
        "department_code": "DEP_GER",
        "department_name": "Geriatrics",
    },
]

PROVIDER_COLUMNS = [
    "provider_code",
    "provider_name",
    "provider_type",
    "specialty",
    "department_code",
    "department_name",
    "active_flag",
]


def _provider_row(provider: dict[str, str]) -> dict[str, str]:
    return {
        "provider_code": provider["code"],
        "provider_name": f"{provider['first_name']} {provider['last_name']}",
        "provider_type": provider["provider_type"],
        "specialty": provider["specialty"],
        "department_code": provider["department_code"],
        "department_name": provider["department_name"],
        "active_flag": "Y",
    }


def generate_providers() -> pd.DataFrame:
    providers = [
        _provider_row(provider)
        for provider in SURGEONS + ANESTHESIOLOGISTS + ATTENDING_PHYSICIANS
    ]
    return pd.DataFrame(providers, columns=PROVIDER_COLUMNS)