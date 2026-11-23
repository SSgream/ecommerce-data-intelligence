from pathlib import Path
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

ZIP_FILE = RAW_DIR / "store-sales-time-series-forecasting.zip"

REQUIRED_FILES = [
    "train.csv",
    "test.csv",
    "stores.csv",
    "transactions.csv",
    "oil.csv",
    "holidays_events.csv",
]


def ingest_dataset():

    print("=" * 50)
    print("DATA INGESTION")
    print("=" * 50)

    if not ZIP_FILE.exists():
        raise FileNotFoundError(
            f"Dataset archive not found: {ZIP_FILE}"
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    missing_files = [
        filename
        for filename in REQUIRED_FILES
        if not (RAW_DIR / filename).is_file()
        or (RAW_DIR / filename).stat().st_size == 0
    ]

    if not missing_files:
        print("All required CSV files already exist.")
        print("Extraction skipped.")

    else:
        print(f"Missing files: {missing_files}")

        with ZipFile(ZIP_FILE, "r") as archive:

            archive_files = set(archive.namelist())

            for filename in missing_files:

                if filename not in archive_files:
                    raise FileNotFoundError(
                        f"{filename} not found inside dataset ZIP."
                    )

                destination = RAW_DIR / filename
                temporary = RAW_DIR / f"{filename}.tmp"

                try:
                    with archive.open(filename) as source:
                        with temporary.open("wb") as target:
                            while chunk := source.read(1024 * 1024):
                                target.write(chunk)

                    if temporary.stat().st_size == 0:
                        raise ValueError(
                            f"{filename} is empty after extraction."
                        )

                    temporary.replace(destination)

                finally:
                    if temporary.exists():
                        temporary.unlink()

                print(f"Extracted: {filename}")

    print("\nValidating raw dataset...")

    for filename in REQUIRED_FILES:

        file_path = RAW_DIR / filename

        if not file_path.is_file() or file_path.stat().st_size == 0:
            raise FileNotFoundError(
                f"Dataset validation failed: {filename}"
            )

        print(f"OK - {filename}")

    print("\nData ingestion completed successfully!")


if __name__ == "__main__":
    ingest_dataset()