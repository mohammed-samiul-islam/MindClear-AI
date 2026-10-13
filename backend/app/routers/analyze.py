from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..ai_service import analyze_text_to_tasks_with_source
from ..dependencies import get_db, get_session_id

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=schemas.AnalyzeResponse)
async def analyze(
    request: schemas.AnalyzeRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
):
    try:
        task_creates, source = await analyze_text_to_tasks_with_source(request.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    conversion = models.Conversion(raw_input=request.text, session_id=session_id, source=source)
    db.add(conversion)
    db.flush()

    tasks = []
    for tc in task_creates:
        task = models.Task(
            session_id=session_id,
            conversion_id=conversion.id,
            task=tc.task,
            category=tc.category,
            priority=tc.priority,
            deadline=tc.deadline,
        )
        db.add(task)
        tasks.append(task)

    db.commit()
    for task in tasks:
        db.refresh(task)

    return schemas.AnalyzeResponse(
        conversion_id=str(conversion.id),
        source=source,
        tasks=[schemas.TaskRead.model_validate(task) for task in tasks],
    )
