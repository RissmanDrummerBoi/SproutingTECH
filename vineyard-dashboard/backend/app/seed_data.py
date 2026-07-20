"""
Populates the database with a handful of vineyard blocks and 21 days of
synthetic ETo/ETa data so the dashboard has something to show during judging.

Run with:  python -m app.seed_data
"""
import random
from datetime import date, timedelta

from .database import SessionLocal, engine, Base
from . import models
from .recommendations import evaluate

Base.metadata.create_all(bind=engine)

BLOCKS = [
    dict(name="Block A - Chenin", variety="Chenin Blanc", area_ha=4.2,
         latitude=-33.9321, longitude=18.8602, soil_type="Sandy loam", planted_year=2011),
    dict(name="Block B - Syrah", variety="Syrah", area_ha=3.1,
         latitude=-33.9298, longitude=18.8570, soil_type="Clay loam", planted_year=2008),
    dict(name="Block C - Sauvignon Blanc", variety="Sauvignon Blanc", area_ha=5.6,
         latitude=-33.9350, longitude=18.8631, soil_type="Decomposed granite", planted_year=2015),
    dict(name="Block D - Cabernet", variety="Cabernet Sauvignon", area_ha=6.0,
         latitude=-33.9275, longitude=18.8544, soil_type="Sandy clay", planted_year=2005),
]


def run():
    db = SessionLocal()
    try:
        if db.query(models.Block).count() > 0:
            print("Blocks already exist — skipping seed.")
            return

        blocks = []
        for b in BLOCKS:
            block = models.Block(**b)
            db.add(block)
            blocks.append(block)
        db.commit()
        for block in blocks:
            db.refresh(block)

        today = date.today()
        for block in blocks:
            # Give each block its own baseline stress tendency for variety.
            baseline_ratio = random.uniform(0.65, 0.98)
            for i in range(21, -1, -1):
                d = today - timedelta(days=i)
                eto = round(random.uniform(4.5, 7.5), 2)
                noise = random.uniform(-0.08, 0.08)
                eta = round(max(eto * (baseline_ratio + noise), 0.5), 2)
                pressure_bomb = round(random.uniform(-1.6, -0.6), 2) if i % 4 == 0 else None

                computed = evaluate(eto, eta, pressure_bomb)
                db.add(models.DailyReading(
                    block_id=block.id,
                    date=d,
                    eto_mm=eto,
                    eta_mm=eta,
                    kc=round(eta / eto, 2) if eto else None,
                    fruitlook_eta_mm=round(eta * random.uniform(0.95, 1.05), 2),
                    pressure_bomb_mpa=pressure_bomb,
                    **computed,
                ))
        db.commit()
        print(f"Seeded {len(blocks)} blocks with 22 days of readings each.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
