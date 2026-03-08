from datetime import date, datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


CategoryType = Literal["Work", "Personal", "Health", "Finance", "Other"]
PriorityType = Literal["High", "Medium", "Low"]


class TaskBase(BaseModel):
    task: str = Field(..., description="Task description")
    category: CategoryType
    priority: PriorityType
    deadline: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: UUID
    conversion_id: UUID
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversionRead(BaseModel):
    id: UUID
    raw_input: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversionWithTasks(BaseModel):
    id: UUID
    raw_input: str
    created_at: datetime
    tasks: List[TaskRead]

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    completed: Optional[bool] = None


class TasksListResponse(BaseModel):
    tasks: List[TaskRead]


class ConversionListItem(BaseModel):
    id: UUID
    raw_input: str
    created_at: datetime
    task_count: int

    class Config:
        from_attributes = True


class ConversionsListResponse(BaseModel):
    conversions: List[ConversionListItem]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw brain dump text from the user")


class AnalyzeResponse(BaseModel):
    conversion_id: str
    tasks: List[TaskRead]

