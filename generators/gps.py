import pandas as pd

from .config import N_GPS
from .faker_instance import fake
from .helpers import introduce_case_noise


def generate_gps(n: int = N_GPS) -> pd.DataFrame:
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

    return pd.DataFrame(gps)