from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_session_id

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("", response_model=schemas.ConversionsListResponse)
def list_conversions(db: Session = Depends(get_db), session_id: str = Depends(get_session_id)):
    rows = (
        db.query(
            models.Conversion.id,
            models.Conversion.raw_input,
            models.Conversion.created_at,
            func.count(models.Task.id).label("task_count"),
        )
        .outerjoin(models.Task, models.Task.conversion_id == models.Conversion.id)
        .filter(models.Conversion.session_id == session_id)
        .group_by(models.Conversion.id, models.Conversion.raw_input, models.Conversion.created_at)
        .order_by(models.Conversion.created_at.desc())
        .all()
    )
    return schemas.ConversionsListResponse(
        conversions=[
            schemas.ConversionListItem(
                id=r.id, raw_input=r.raw_input, created_at=r.created_at, task_count=r.task_count
            )
            for r in rows
        ]
    )
