from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship
from .database import Base


class Block(Base):
    """A single vineyard block (management unit)."""
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    variety = Column(String, nullable=True)          # e.g. "Chenin Blanc"
    area_ha = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    soil_type = Column(String, nullable=True)
    planted_year = Column(Integer, nullable=True)

    readings = relationship(
        "DailyReading", back_populates="block", cascade="all, delete-orphan"
    )


class DailyReading(Base):
    """One day's ET / irrigation record for a block."""
    __tablename__ = "daily_readings"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    eto_mm = Column(Float, nullable=False)   # reference evapotranspiration
    eta_mm = Column(Float, nullable=False)   # actual evapotranspiration
    kc = Column(Float, nullable=True)        # crop coefficient, if available

    # Validation inputs (optional, may be null on days without field data)
    fruitlook_eta_mm = Column(Float, nullable=True)
    pressure_bomb_mpa = Column(Float, nullable=True)

    # Computed by the recommendation engine at write time
    stress_ratio = Column(Float, nullable=True)      # eta / eto
    stress_flag = Column(String, nullable=True)       # "none" | "mild" | "severe"
    action = Column(String, nullable=True)             # "irrigate" | "hold"
    recommended_mm = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    block = relationship("Block", back_populates="readings")
