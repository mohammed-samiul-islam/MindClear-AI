from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..ai_service import analyze_text_to_tasks
from ..database import get_db

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=schemas.AnalyzeResponse)
async def analyze(request: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        task_creates = await analyze_text_to_tasks(request.text)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI processing failed: {e}",
        )

    conversion = models.Conversion(raw_input=request.text)
    db.add(conversion)
    db.flush()

    tasks = []
    for tc in task_creates:
        task = models.Task(
            conversion_id=conversion.id,
            task=tc.task,
            category=tc.category,
            priority=tc.priority,
            deadline=tc.deadline,
        )
        db.add(task)
        tasks.append(task)

    db.commit()
    db.refresh(conversion)
    for task in tasks:
        db.refresh(task)

    return schemas.AnalyzeResponse(
        conversion_id=str(conversion.id),
        tasks=[schemas.TaskRead.model_validate(task) for task in tasks],
    )
