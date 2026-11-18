
from pathlib import Path
import csv

DATA_DIR = Path("data/raw")

print("=" * 60)
print("DATASET FILE INSPECTION")
print("=" * 60)

for file in sorted(DATA_DIR.iterdir()):
    if file.is_file():
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"{file.name:<30} {size_mb:>10.2f} MB")

print("\n" + "=" * 60)
print("CSV STRUCTURE INSPECTION")
print("=" * 60)

for file in sorted(DATA_DIR.glob("*.csv")):
    print(f"\nDataset: {file.name}")

    with file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)

        columns = next(reader, [])
        print("Columns:", columns)

        print("Sample data:")
        for i, row in enumerate(reader):
            print(row)
            if i == 2:
                break
