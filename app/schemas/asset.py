from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.asset import AssetType, AssetStatus


class AssetCreate(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: str
    tags: list[str] = []
    asset_metadata: dict = {}


class AssetUpdate(BaseModel):
    type: Optional[AssetType] = None
    value: Optional[str] = None
    status: Optional[AssetStatus] = None
    source: Optional[str] = None
    tags: Optional[list[str]] = None
    asset_metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str
    status: AssetStatus
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: list[str]
    asset_metadata: dict

    class Config:
        from_attributes = True

class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int