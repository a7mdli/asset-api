from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetType, AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate


def create_asset(db: Session, asset: AssetCreate, id: str | None):
    data = asset.model_dump()
    data["asset_metadata"] = data.pop("metadata")
    db_asset = Asset(
        id=id if id else str(uuid4()),
        **data
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_assets(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    asset_type: AssetType | None = None,
    status: AssetStatus | None = None,
    tag: str | None = None,
    value: str | None = None,
    sort_by: str = "last_seen",
    sort_order: str = "desc",
):

    query = db.query(Asset)

    # Filtering

    if asset_type:
        query = query.filter(Asset.type == asset_type)

    if status:
        query = query.filter(Asset.status == status)

    if tag:
        query = query.filter(Asset.tags.any(tag))

    if value:
        query = query.filter(Asset.value.ilike(f"%{value}%"))

    # Sorting

    allowed_columns = {
        "value": Asset.value,
        "type": Asset.type,
        "status": Asset.status,
        "first_seen": Asset.first_seen,
        "last_seen": Asset.last_seen,
        "source": Asset.source,
    }

    column = allowed_columns.get(sort_by, Asset.last_seen)

    if sort_order == "asc":
        query = query.order_by(asc(column))
    else:
        query = query.order_by(desc(column))

    total = query.count()

    assets = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": assets,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_asset(db: Session, asset_id):
    return db.query(Asset).filter(Asset.id == asset_id).first()


def update_asset(db: Session, asset_id, update: AssetUpdate):
    asset = get_asset(db, asset_id)
    if not asset:
        return None
    data = update.model_dump(exclude_unset=True)
    if "metadata" in data:
        data["asset_metadata"] = data.pop("metadata")
    for key, value in data.items():
        setattr(asset, key, value)
        asset.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id):
    asset = get_asset(db, asset_id)
    if not asset:
        return None
    db.delete(asset)
    db.commit()
    return asset
