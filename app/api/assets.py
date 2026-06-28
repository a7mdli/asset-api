from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.asset import *
from app.schemas.asset import *

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/")
def create(
    asset: AssetCreate,
    id: str | None = Query(None),
    db: Session = Depends(get_db)
):
    return create_asset(db, asset, id)

@router.get("/", response_model=AssetListResponse)
def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),

    asset_type: AssetType | None = Query(None, alias="type"),
    status: AssetStatus | None = None,

    tag: str | None = None,
    value: str | None = None,

    sort_by: str = Query("last_seen"),
    sort_order: str = Query("desc"),

    db: Session = Depends(get_db),
):
    return get_assets(
        db,
        page,
        page_size,
        asset_type,
        status,
        tag,
        value,
        sort_by,
        sort_order,
    )


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

@router.post("/import")
def bulk_import(
    assets: list[AssetImport],
    db: Session = Depends(get_db)
):
    return import_assets(db, assets)

@router.patch("/{asset_id}/stale", response_model=AssetResponse)
def mark_stale(
    asset_id: UUID,
    db: Session = Depends(get_db),
):
    asset = mark_asset_stale(db, asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset