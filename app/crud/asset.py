from datetime import datetime

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


def create_asset(db: Session, asset: AssetCreate):
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def get_assets(db: Session):
    return db.query(Asset).all()


def get_asset(db: Session, asset_id):
    return db.query(Asset).filter(Asset.id == asset_id).first()


def update_asset(db: Session, asset_id, update: AssetUpdate):
    asset = get_asset(db, asset_id)
    if not asset:
        return None
    for key, value in update.model_dump(exclude_unset=True).items():
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
