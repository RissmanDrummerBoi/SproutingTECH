"""
FruitLook has no public API — it's a farmer-facing web portal
(fruitlook.co.za) that's also currently running a reduced/paused service,
with data available as weekly exports rather than programmatic access.

This importer takes a CSV exported from the FruitLook portal and attaches
its actual-ET figures to matching DailyReading rows, purely for
validation/calibration of the modeled ETa (see crop_coefficients.py) — it
does not overwrite eta_mm itself, since FruitLook's cadence is weekly
while our model runs daily.

Expected CSV columns (rename via the `column_map` argument if your export
differs):
    block_name, date, eta_mm

Usage:
    python -m app.fruitlook_import path/to/export.csv
"""
import csv
import sys
from datetime import date

from .database import SessionLocal
from . import models


def import_csv(path: str, column_map: dict | None = None) -> dict:
    cols = column_map or {"block_name": "block_name", "date": "date", "eta_mm": "eta_mm"}
    db = SessionLocal()
    summary = {"matched": 0, "unmatched_block": 0, "unmatched_date": 0}

    try:
        blocks_by_name = {b.name: b for b in db.query(models.Block).all()}

        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                block_name = row[cols["block_name"]].strip()
                block = blocks_by_name.get(block_name)
                if not block:
                    summary["unmatched_block"] += 1
                    continue

                row_date = date.fromisoformat(row[cols["date"]].strip())
                reading = (
                    db.query(models.DailyReading)
                    .filter(
                        models.DailyReading.block_id == block.id,
                        models.DailyReading.date == row_date,
                    )
                    .first()
                )
                if not reading:
                    summary["unmatched_date"] += 1
                    continue

                reading.fruitlook_eta_mm = float(row[cols["eta_mm"]])
                summary["matched"] += 1

        db.commit()
        return summary
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.fruitlook_import path/to/export.csv")
        sys.exit(1)
    print(import_csv(sys.argv[1]))
