from fastapi import APIRouter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.asset import *
from app.schemas.asset import *
from app.crud.relationships import *
from app.schemas.relationship import *

router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"]
)

@router.post("/", response_model=RelationshipResponse)
def create(
    relationship: RelationshipCreate,
    db: Session = Depends(get_db)
):
    return create_relationship(db, relationship)


@router.get("/", response_model=RelationshipListResponse)
def list_relationships(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    relationship_type: RelationshipType | None = Query(
        None,
        alias="type"
    ),
    db: Session = Depends(get_db),
):
    return get_relationships(
        db=db,
        page=page,
        page_size=page_size,
        relationship_type=relationship_type,
    )

@router.delete("/{relationship_id}")
def delete(
    relationship_id: UUID,
    db: Session = Depends(get_db)
):
    rel = delete_relationship(db, relationship_id)

    if rel is None:
        raise HTTPException(404)

    return {"message": "Deleted"}

@router.get("/assets/{asset_id}/relationships")
def related_assets(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    return {
        "asset_id": asset_id,
        "relationships": get_related_assets(db, asset_id)
    }