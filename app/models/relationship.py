import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.core.database import Base

class RelationshipType(str, enum.Enum):
    SUBDOMAIN_OF = "subdomain_of"
    HOSTS = "hosts"                    # ip -> service
    RESOLVES_TO = "resolves_to"        # subdomain -> ip
    RESOLVED_BY = "resolved_by"        # ip -> subdomain (optional)
    SECURED_BY = "secured_by"          # domain/subdomain -> certificate
    RUNS = "runs"                      # subdomain/service -> technology


class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    first_asset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )

    second_asset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )

    relationship_type = Column(
        Enum(RelationshipType),
        nullable=False
    )