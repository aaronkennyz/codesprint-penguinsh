from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import Person, Encounter, DerivedResult, Worker
from ..schemas import WorkerCreateIn, WorkerOut, PersonIn, PersonOut
from ..security import require_perm, hash_password
from ..rbac import Role

router = APIRouter(prefix="/api", tags=["admin"])

@router.get("/dashboard/coverage", dependencies=[Depends(require_perm("dashboards:view"))])
def coverage(db: Session = Depends(get_db)):
    total_people = db.query(func.count(Person.id)).scalar()
    screened = db.query(func.count(Encounter.id)).filter(Encounter.submitted_at.isnot(None)).scalar()
    return {"total_people": total_people, "screened": screened}

@router.get("/dashboard/verification-rates", dependencies=[Depends(require_perm("dashboards:view"))])
def verification_rates(db: Session = Depends(get_db)):
    total = db.query(func.count(Encounter.id)).filter(Encounter.submitted_at.isnot(None)).scalar()
    verified = db.query(func.count(Encounter.id)).filter(Encounter.status == "VERIFIED").scalar()
    return {"total_submitted": total, "verified": verified, "verified_rate": (verified / total) if total else 0.0}

@router.get("/dashboard/overdue", dependencies=[Depends(require_perm("dashboards:view"))])
def overdue_stub():
    # Real overdue is computed client-side by due engine offline; server can later aggregate derived_results.followup_date.
    return {"note": "Overdue list is computed offline on device from rules.json + latest derived results."}

@router.get("/export/csv", dependencies=[Depends(require_perm("export:csv"))])
def export_csv_stub():
    return {"note": "Implement CSV streaming export (people, encounters, results). Keep it paged and gzip."}

@router.post("/admin/workers", response_model=WorkerOut, dependencies=[Depends(require_perm("admin:manage"))])
def create_worker(body: WorkerCreateIn, db: Session = Depends(get_db)):
    try:
        role = Role(body.role.upper())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid role")

    if role == Role.PATIENT:
        raise HTTPException(status_code=400, detail="Use patient endpoint for patient accounts")

    existing = db.query(Worker).filter(Worker.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    w = Worker(
        username=body.username,
        password_hash=hash_password(body.password),
        role=role.value,
        display_name=body.display_name,
        phone=body.phone,
        assigned_villages_json=body.assigned_villages or [],
        is_active=True,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return WorkerOut(
        id=w.id,
        username=w.username,
        role=w.role,
        display_name=w.display_name,
        phone=w.phone,
        assigned_villages=w.assigned_villages_json or [],
        is_active=w.is_active,
        updated_at=w.updated_at,
    )

@router.post("/admin/patients", response_model=PersonOut, dependencies=[Depends(require_perm("admin:manage"))])
def create_patient(body: PersonIn, db: Session = Depends(get_db)):
    p = Person(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return PersonOut(**body.model_dump(), id=p.id, updated_at=p.updated_at)
