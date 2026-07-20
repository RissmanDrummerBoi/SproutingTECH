from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BlockBase(BaseModel):
    name: str
    variety: Optional[str] = None
    area_ha: float
    latitude: float
    longitude: float
    soil_type: Optional[str] = None
    planted_year: Optional[int] = None


class BlockCreate(BlockBase):
    pass


class Block(BlockBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ReadingCreate(BaseModel):
    date: date
    eto_mm: float
    eta_mm: float
    kc: Optional[float] = None
    fruitlook_eta_mm: Optional[float] = None
    pressure_bomb_mpa: Optional[float] = None


class Reading(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    block_id: int
    date: date
    eto_mm: float
    eta_mm: float
    kc: Optional[float]
    fruitlook_eta_mm: Optional[float]
    pressure_bomb_mpa: Optional[float]
    stress_ratio: Optional[float]
    stress_flag: Optional[str]
    action: Optional[str]
    recommended_mm: Optional[float]
    created_at: Optional[datetime]


class BlockWithLatest(Block):
    latest_reading: Optional[Reading] = None
