from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.asset import *
from app.schemas.asset import *

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/", response_model=AssetResponse)
def create(asset: AssetCreate, db: Session = Depends(get_db)):
    return create_asset(db, asset)


@router.get("/", response_model=list[AssetResponse])
def get_all(db: Session = Depends(get_db)):
    return get_assets(db)


@router.get("/{asset_id}", response_model=AssetResponse)
def get(asset_id: UUID, db: Session = Depends(get_db)):
    asset = get_asset(db, asset_id)
    if not asset:
        raise HTTPException(404)
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update(asset_id: UUID, update: AssetUpdate, db: Session = Depends(get_db)):
    asset = update_asset(db, asset_id, update)
    if not asset:
        raise HTTPException(404)
    return asset


@router.delete("/{asset_id}")
def delete(asset_id: UUID, db: Session = Depends(get_db)):
    asset = delete_asset(db, asset_id)
    if not asset:
        raise HTTPException(404)
    return {"message": "Deleted"}
