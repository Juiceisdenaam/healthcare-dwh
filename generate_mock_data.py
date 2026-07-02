from pathlib import Path
import random

import numpy as np

from generators.config import RANDOM_SEED, SOURCE_SYSTEMS
from generators.gps import generate_gps
from generators.insurances import generate_insurances
from generators.patients import generate_patients


def main() -> None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Generating Mock Data ===")
    
    print("Generating insurances...")
    insurances_df = generate_insurances(insert_to_postgres=True)
    print(f"✓ Insurances generated and inserted: {len(insurances_df)} rows")
    
    print("Generating GPS...")
    gps_df = generate_gps(insert_to_postgres=True)
    print(f"✓ GPS generated and inserted: {len(gps_df)} rows")
    
    print("Generating patients...")
    patients_df = generate_patients(gps_df, insurances_df, insert_to_postgres=False)
    print(f"✓ Patients generated and inserted: {len(patients_df)} rows")

    print("\n=== Exporting to CSV ===")
    insurances_df.to_csv(output_dir / "insurances.csv", index=False)
    print(f"✓ {output_dir / 'insurances.csv'}: {len(insurances_df)} rows")
    
    gps_df.to_csv(output_dir / "gps.csv", index=False)
    print(f"✓ {output_dir / 'gps.csv'}: {len(gps_df)} rows")
    
    patients_df.to_csv(output_dir / "patients.csv", index=False)
    print(f"✓ {output_dir / 'patients.csv'}: {len(patients_df)} rows")

    for source_system in SOURCE_SYSTEMS:
        source_df = patients_df[patients_df["source_system"] == source_system].copy()
        source_file = output_dir / f"patients_{source_system.lower()}.csv"
        source_df.to_csv(source_file, index=False)
        print(f"✓ {source_file}: {len(source_df)} rows")
    
    print("\n=== Complete ===")


if __name__ == "__main__":
    main()