from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.relationship import RelationshipType

class RelationshipCreate(BaseModel):
    first_asset_id: UUID
    second_asset_id: UUID
    relationship_type: RelationshipType


class RelationshipResponse(BaseModel):
    id: UUID
    first_asset_id: UUID
    second_asset_id: UUID
    relationship_type: RelationshipType

    class Config:
        from_attributes = True

class RelationshipListResponse(BaseModel):
    items: list[RelationshipResponse]
    total: int
    page: int
    page_size: int