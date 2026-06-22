# healthcare-dwh

This repository is split into two concerns:

- Python generators that create realistic raw healthcare source data
- A dbt project where you can stage, match, and model that data into a warehouse

## Structure

```text
healthcare-dwh/
|-- data/
|   `-- raw/
|-- dbt/
|   |-- dbt_project.yml
|   `-- models/
|       |-- staging/
|       |-- intermediate/
|       `-- marts/
|-- generators/
|   |-- config.py
|   |-- faker_instance.py
|   |-- gps.py
|   |-- helpers.py
|   |-- insurances.py
|   `-- patients.py
|-- generate_mock_data.py
|-- main.py
`-- README.md
```

## Python generators

- `generate_mock_data.py` is the main entrypoint for creating mock source files.
- `main.py` remains as a thin compatibility wrapper.
- `generators/patients.py` contains patient generation and duplicate scenarios.
- `generators/gps.py` and `generators/insurances.py` generate source reference data.

Generated source files are written to `data/raw/`:

- `patients.csv`
- `gps.csv`
- `insurances.csv`

Run the generator with:

```bash
python generate_mock_data.py
```

## dbt project

The dbt project lives under `dbt/` and already has the standard model layers:

- `models/staging` for source cleanup and standardization
- `models/intermediate` for match logic and survivorship rules
- `models/marts` for final dimensions and facts

Suggested next steps:

1. Generate mock data into `data/raw/`
2. Load the CSV files into your raw database schema
3. Build `stg_*` models in dbt
4. Add patient matching logic in `intermediate`
5. Build `dim_patient` in `marts`