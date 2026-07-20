from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from .recommendations import evaluate


def list_blocks(db: Session):
    return db.query(models.Block).order_by(models.Block.name).all()


def get_block(db: Session, block_id: int):
    return db.query(models.Block).filter(models.Block.id == block_id).first()


def create_block(db: Session, block: schemas.BlockCreate):
    db_block = models.Block(**block.model_dump())
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block


def latest_reading(db: Session, block_id: int):
    return (
        db.query(models.DailyReading)
        .filter(models.DailyReading.block_id == block_id)
        .order_by(desc(models.DailyReading.date))
        .first()
    )


def list_readings(db: Session, block_id: int, limit: int = 30):
    return (
        db.query(models.DailyReading)
        .filter(models.DailyReading.block_id == block_id)
        .order_by(desc(models.DailyReading.date))
        .limit(limit)
        .all()[::-1]  # chronological order for charting
    )


def create_reading(db: Session, block_id: int, reading: schemas.ReadingCreate):
    computed = evaluate(
        eto_mm=reading.eto_mm,
        eta_mm=reading.eta_mm,
        pressure_bomb_mpa=reading.pressure_bomb_mpa,
    )
    db_reading = models.DailyReading(
        block_id=block_id,
        **reading.model_dump(),
        **computed,
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading
