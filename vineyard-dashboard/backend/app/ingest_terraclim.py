"""
Pulls daily ETo from TerraClim for every block, models ETa via the Kc
curve, and writes DailyReading rows through the normal recommendation
pipeline (so stress flags / actions are computed exactly as they are for
manually-entered readings).

Run directly:
    python -m app.ingest_terraclim --days 7

Or trigger via the API: POST /api/ingest/terraclim?days=7
"""
import argparse
from datetime import date, timedelta

from .database import SessionLocal
from . import models, schemas, crud
from .crop_coefficients import model_eta
from .integrations.terraclim import TerraClimClient


def run(days: int = 7, db=None) -> dict:
    owns_session = db is None
    db = db or SessionLocal()
    summary = {"blocks_processed": 0, "readings_written": 0, "skipped_existing": 0}

    try:
        blocks = db.query(models.Block).all()
        if not blocks:
            return summary

        client = TerraClimClient()
        end = date.today() - timedelta(days=1)   # yesterday: today's ETo isn't final yet
        start = end - timedelta(days=days - 1)

        points = [(b.latitude, b.longitude) for b in blocks]
        eto_by_point = client.get_daily_eto(points, start, end)

        for idx, block in enumerate(blocks):
            existing_dates = {
                r.date.isoformat()
                for r in db.query(models.DailyReading)
                .filter(models.DailyReading.block_id == block.id)
                .all()
            }
            for iso_day, eto_mm in sorted(eto_by_point.get(idx, {}).items()):
                if iso_day in existing_dates:
                    summary["skipped_existing"] += 1
                    continue
                d = date.fromisoformat(iso_day)
                eta_mm = model_eta(eto_mm, d)
                crud.create_reading(
                    db,
                    block.id,
                    schemas.ReadingCreate(date=d, eto_mm=eto_mm, eta_mm=eta_mm),
                )
                summary["readings_written"] += 1
            summary["blocks_processed"] += 1

        return summary
    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest TerraClim ETo for all blocks")
    parser.add_argument("--days", type=int, default=7, help="How many days back to pull")
    args = parser.parse_args()
    result = run(days=args.days)
    print(result)
