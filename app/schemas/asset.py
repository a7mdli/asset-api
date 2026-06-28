from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.asset import AssetType, AssetStatus


class AssetCreate(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: str
    tags: list[str] = []
    metadata: dict = {}


class AssetUpdate(BaseModel):
    type: Optional[AssetType] = None
    value: Optional[str] = None
    status: Optional[AssetStatus] = None
    source: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str
    status: AssetStatus
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: list[str]
    metadata: dict = Field(validation_alias="asset_metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int