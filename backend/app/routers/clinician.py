from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db import get_db
from ..models import Encounter, Person, DerivedResult, AuditLog
from ..schemas import QueueItem
from ..security import require_perm, get_principal

router = APIRouter(prefix="/api", tags=["clinician"])

@router.get("/queue", response_model=list[QueueItem], dependencies=[Depends(require_perm("queue:view"))])
def queue(rag: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Encounter, Person, DerivedResult)
        .join(Person, Person.id == Encounter.person_id)
        .join(DerivedResult, DerivedResult.encounter_id == Encounter.id)
        .filter(DerivedResult.rag == rag, Encounter.status.in_(["VERIFIED", "UNVERIFIED"]))
        .order_by(Encounter.submitted_at.desc())
        .limit(200).all()
    )
    out = []
    for enc, p, dr in rows:
        out.append(QueueItem(encounter_id=enc.id, person_id=p.id, person_name=p.full_name, rag=dr.rag, status=enc.status, submitted_at=enc.submitted_at))
    return out

@router.get("/encounters/unverified", response_model=list[QueueItem], dependencies=[Depends(require_perm("unverified:view"))])
def unverified(db: Session = Depends(get_db)):
    rows = (
        db.query(Encounter, Person, DerivedResult)
        .join(Person, Person.id == Encounter.person_id)
        .join(DerivedResult, DerivedResult.encounter_id == Encounter.id)
        .filter(Encounter.status == "UNVERIFIED")
        .order_by(Encounter.submitted_at.desc())
        .limit(200).all()
    )
    return [QueueItem(encounter_id=e.id, person_id=p.id, person_name=p.full_name, rag=dr.rag, status=e.status, submitted_at=e.submitted_at) for e,p,dr in rows]

@router.post("/encounters/{encounter_id}/approve", dependencies=[Depends(require_perm("encounter:approve"))])
def approve(encounter_id: int, db: Session = Depends(get_db), pr=Depends(get_principal)):
    enc = db.get(Encounter, encounter_id)
    if not enc:
        raise HTTPException(404, "Not found")
    if enc.status != "UNVERIFIED":
        raise HTTPException(409, "Not unverified")
    enc.status = "VERIFIED"
    enc.verified_at = enc.verified_at  # clinician approval time could be stored separately if desired
    db.add(AuditLog(actor_worker_id=pr.worker.id if pr.worker else None, action="approve", entity="encounter", entity_id=str(encounter_id)))
    db.commit()
    return {"ok": True}

@router.post("/encounters/{encounter_id}/reject", dependencies=[Depends(require_perm("encounter:reject"))])
def reject(encounter_id: int, db: Session = Depends(get_db), pr=Depends(get_principal)):
    enc = db.get(Encounter, encounter_id)
    if not enc:
        raise HTTPException(404, "Not found")
    if enc.status != "UNVERIFIED":
        raise HTTPException(409, "Not unverified")
    # Keep record but mark rejected via audit; production: add status REJECTED.
    db.add(AuditLog(actor_worker_id=pr.worker.id if pr.worker else None, action="reject", entity="encounter", entity_id=str(encounter_id)))
    db.commit()
    return {"ok": True}
