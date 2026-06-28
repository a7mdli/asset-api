from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.relationship import AssetRelationship, RelationshipType
from app.schemas.relationship import RelationshipCreate
from app.models.asset import Asset

def create_relationship(db, rel: RelationshipCreate):

    relationship = AssetRelationship(**rel.model_dump())

    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    return relationship

from sqlalchemy.orm import Session

def get_relationships(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    relationship_type: RelationshipType | None = None,
):

    query = db.query(AssetRelationship)

    if relationship_type:
        query = query.filter(
            AssetRelationship.relationship_type == relationship_type
        )

    total = query.count()

    relationships = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": relationships,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

def delete_relationship(db, relationship_id):

    rel = db.get(AssetRelationship, relationship_id)

    if rel is None:
        return None

    db.delete(rel)
    db.commit()

    return rel

def get_related_assets(db, asset_id):

    relationships = (
        db.query(AssetRelationship)
        .filter(
            or_(
                AssetRelationship.first_asset_id == asset_id,
                AssetRelationship.second_asset_id == asset_id
            )
        )
        .all()
    )

    result = []

    for rel in relationships:

        other_id = (
            rel.second_asset_id
            if rel.first_asset_id == asset_id
            else rel.first_asset_id
        )

        other_asset = db.get(Asset, other_id)

        result.append({
            "relationship_type": rel.relationship_type,
            "asset": other_asset
        })

    return result