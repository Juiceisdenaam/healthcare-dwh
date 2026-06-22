from pathlib import Path
import random

import numpy as np

from generators.config import RANDOM_SEED
from generators.gps import generate_gps
from generators.insurances import generate_insurances
from generators.patients import generate_patients


def main() -> None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    insurances_df = generate_insurances()
    gps_df = generate_gps()
    patients_df = generate_patients(gps_df, insurances_df)

    insurances_df.to_csv(output_dir / "insurances.csv", index=False)
    gps_df.to_csv(output_dir / "gps.csv", index=False)
    patients_df.to_csv(output_dir / "patients.csv", index=False)

    print("Generated:")
    print(f"- {output_dir / 'insurances.csv'}: {len(insurances_df)} rows")
    print(f"- {output_dir / 'gps.csv'}: {len(gps_df)} rows")
    print(f"- {output_dir / 'patients.csv'}: {len(patients_df)} rows")


if __name__ == "__main__":
    main()