from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db, engine
from .. import models, schemas, crud, calendar_service, scheduler

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/api/tasks", response_model=List[schemas.TaskOut])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)


@router.post("/api/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@router.put("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id, task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.post("/api/tasks/{task_id}/complete", response_model=schemas.TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.complete_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.get("/api/calendar-events")
def get_calendar_events(days: int = 7):
    return calendar_service.get_upcoming_events(days=days)


@router.get("/api/schedule")
def get_schedule(days: int = 7, db: Session = Depends(get_db)):
    events = calendar_service.get_upcoming_events(days=days)
    free_slots = calendar_service.find_free_slots(events, days=days)
    tasks = [task for task in crud.get_tasks(db) if task.status != "completed"]
    scheduled = scheduler.schedule_tasks(tasks, free_slots)
    result = []
    for task, start, end in scheduled:
        result.append({
            "task_id": task.id,
            "title": task.title,
            "start": start,
            "end": end,
        })
    return result
