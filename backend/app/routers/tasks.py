from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=schemas.TasksListResponse)
def list_tasks(
    db: Session = Depends(get_db),
    category: str | None = Query(None, description="Filter by category"),
    priority: str | None = Query(None, description="Filter by priority"),
    completed: bool | None = Query(None, description="Filter by completed status"),
    conversion_id: UUID | None = Query(None, description="Filter by conversion (brain dump)"),
):
    q = db.query(models.Task)
    if category is not None:
        q = q.filter(models.Task.category == category)
    if priority is not None:
        q = q.filter(models.Task.priority == priority)
    if completed is not None:
        q = q.filter(models.Task.completed == completed)
    if conversion_id is not None:
        q = q.filter(models.Task.conversion_id == conversion_id)
    tasks = q.order_by(models.Task.created_at.desc()).all()
    return schemas.TasksListResponse(tasks=[schemas.TaskRead.model_validate(t) for t in tasks])


@router.patch("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: UUID,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.completed is not None:
        task.completed = payload.completed
    db.commit()
    db.refresh(task)
    return schemas.TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
