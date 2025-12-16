"""
Task management endpoints for follow-up actions.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_db
from models import Task


class TaskBase(BaseModel):
    constituent_id: int = Field(..., description="Related constituent ID")
    description: str = Field(..., min_length=3)
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    task_id: int
    status: str

    class Config:
        orm_mode = True


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        constituent_id=task.constituent_id,
        description=task.description,
        due_date=task.due_date,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    constituent_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if constituent_id is not None:
        query = query.filter(Task.constituent_id == constituent_id)
    if status:
        query = query.filter(Task.status == status)
    return query.order_by(Task.due_date.asc().nulls_last()).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.description = data.description
    db_task.due_date = data.due_date
    db.commit()
    db.refresh(db_task)
    return db_task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.status = "completed"
    db.commit()
    db.refresh(db_task)
    return db_task
