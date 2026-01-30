from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Task
from ..schemas import TaskIn, TaskOut, ReminderIn
from ..models import ReminderLog
from ..security import require_perm, get_principal

router = APIRouter(prefix="/api", tags=["tasks"])

@router.post("/tasks", response_model=TaskOut, dependencies=[Depends(require_perm("tasks:create"))])
def create_task(body: TaskIn, db: Session = Depends(get_db), pr=Depends(get_principal)):
    if not pr.worker:
        raise HTTPException(403, "Worker required")
    t = Task(
        person_id=body.person_id,
        encounter_id=body.encounter_id,
        type=body.type,
        status="OPEN",
        due_date=body.due_date,
        notes=body.notes,
        created_by_worker_id=pr.worker.id,
    )
    db.add(t); db.commit(); db.refresh(t)
    return TaskOut(**body.model_dump(), id=t.id, status=t.status)

@router.get("/tasks", response_model=list[TaskOut], dependencies=[Depends(require_perm("queue:view"))])
def list_tasks(status: str = "OPEN", db: Session = Depends(get_db)):
    rows = db.query(Task).filter(Task.status == status).order_by(Task.created_at.desc()).limit(200).all()
    return [TaskOut(
        id=r.id, person_id=r.person_id, encounter_id=r.encounter_id, type=r.type,
        due_date=r.due_date, notes=r.notes, status=r.status
    ) for r in rows]

@router.post("/tasks/{task_id}/close", dependencies=[Depends(require_perm("tasks:close"))])
def close_task(task_id: int, db: Session = Depends(get_db), pr=Depends(get_principal)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Not found")
    t.status = "CLOSED"
    t.closed_by_worker_id = pr.worker.id if pr.worker else None
    t.closed_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}

@router.post("/reminders", dependencies=[Depends(require_perm("reminders:write"))])
def create_reminder(body: ReminderIn, db: Session = Depends(get_db), pr=Depends(get_principal)):
    if not pr.worker:
        raise HTTPException(403, "Worker required")
    r = ReminderLog(person_id=body.person_id, worker_id=pr.worker.id, outcome=body.outcome, notes=body.notes)
    db.add(r); db.commit()
    return {"ok": True}
