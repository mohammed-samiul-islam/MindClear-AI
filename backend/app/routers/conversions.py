from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("", response_model=schemas.ConversionsListResponse)
def list_conversions(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Conversion.id,
            models.Conversion.raw_input,
            models.Conversion.created_at,
            func.count(models.Task.id).label("task_count"),
        )
        .outerjoin(models.Task, models.Task.conversion_id == models.Conversion.id)
        .group_by(models.Conversion.id, models.Conversion.raw_input, models.Conversion.created_at)
        .order_by(models.Conversion.created_at.desc())
        .all()
    )
    conversions = [
        schemas.ConversionListItem(
            id=r.id,
            raw_input=r.raw_input,
            created_at=r.created_at,
            task_count=r.task_count,
        )
        for r in rows
    ]
    return schemas.ConversionsListResponse(conversions=conversions)
