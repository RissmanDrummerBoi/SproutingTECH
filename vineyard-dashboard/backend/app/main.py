from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db
from . import ingest_terraclim
from .integrations.terraclim import TerraClimRateLimitError

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vineyard Irrigation Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/blocks", response_model=List[schemas.BlockWithLatest])
def get_blocks(db: Session = Depends(get_db)):
    blocks = crud.list_blocks(db)
    result = []
    for b in blocks:
        latest = crud.latest_reading(db, b.id)
        item = schemas.BlockWithLatest.model_validate(b)
        item.latest_reading = (
            schemas.Reading.model_validate(latest) if latest else None
        )
        result.append(item)
    return result


@app.post("/api/blocks", response_model=schemas.Block)
def create_block(block: schemas.BlockCreate, db: Session = Depends(get_db)):
    return crud.create_block(db, block)


@app.get("/api/blocks/{block_id}", response_model=schemas.Block)
def get_block(block_id: int, db: Session = Depends(get_db)):
    block = crud.get_block(db, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


@app.get("/api/blocks/{block_id}/readings", response_model=List[schemas.Reading])
def get_readings(block_id: int, limit: int = 30, db: Session = Depends(get_db)):
    if not crud.get_block(db, block_id):
        raise HTTPException(status_code=404, detail="Block not found")
    return crud.list_readings(db, block_id, limit)


@app.post("/api/blocks/{block_id}/readings", response_model=schemas.Reading)
def add_reading(
    block_id: int, reading: schemas.ReadingCreate, db: Session = Depends(get_db)
):
    if not crud.get_block(db, block_id):
        raise HTTPException(status_code=404, detail="Block not found")
    return crud.create_reading(db, block_id, reading)


@app.post("/api/ingest/terraclim")
def trigger_terraclim_ingest(days: int = 7, db: Session = Depends(get_db)):
    """Pull TerraClim ETo for all blocks, model ETa, write readings. See ingest_terraclim.py."""
    try:
        return ingest_terraclim.run(days=days, db=db)
    except TerraClimRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except RuntimeError as e:
        # e.g. missing TERRACLIM_API_TOKEN
        raise HTTPException(status_code=500, detail=str(e))
