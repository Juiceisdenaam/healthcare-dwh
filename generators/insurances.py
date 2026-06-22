import pandas as pd


def generate_insurances() -> pd.DataFrame:
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
    return pd.DataFrame(insurances, columns=["insurance_code", "insurance_name"])