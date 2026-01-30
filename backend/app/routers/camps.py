from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from ..db import get_db
from ..models import Camp
from ..schemas import CampIn, CampOut
from ..security import require_perm, get_principal
from ..rbac import Role

router = APIRouter(prefix="/api", tags=["camps"])

@router.post("/camps", response_model=CampOut, dependencies=[Depends(require_perm("camps:create"))])
def create_camp(body: CampIn, db: Session = Depends(get_db)):
    c = Camp(**body.model_dump())
    db.add(c)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Invalid village_id or camp data")
    db.refresh(c)
    return CampOut(**body.model_dump(), id=c.id, updated_at=c.updated_at)

@router.get("/camps", response_model=list[CampOut])
def list_camps(
    village_id: int,
    from_date: str | None = None,
    updated_since: str | None = None,
    db: Session = Depends(get_db),
    pr = Depends(get_principal),
):
    # Patients can view their village camps; workers limited in UI by assigned villages.
    q = db.query(Camp).filter(Camp.village_id == village_id)
    if from_date:
        q = q.filter(Camp.date >= date.fromisoformat(from_date))
    if updated_since:
        q = q.filter(Camp.updated_at > datetime.fromisoformat(updated_since))
    rows = q.order_by(Camp.date.asc()).limit(200).all()
    return [CampOut(
        id=r.id, village_id=r.village_id, name=r.name, date=r.date,
        start_time=r.start_time, end_time=r.end_time,
        address=r.address, landmark=r.landmark,
        lat=float(r.lat), lng=float(r.lng),
        contact_name=r.contact_name, contact_phone=r.contact_phone,
        services_json=r.services_json, updated_at=r.updated_at
    ) for r in rows]

@router.get("/camps/{camp_id}", response_model=CampOut)
def get_camp(camp_id: int, db: Session = Depends(get_db), pr = Depends(get_principal)):
    r = db.get(Camp, camp_id)
    if not r:
        raise HTTPException(404, "Not found")
    return CampOut(
        id=r.id, village_id=r.village_id, name=r.name, date=r.date,
        start_time=r.start_time, end_time=r.end_time,
        address=r.address, landmark=r.landmark,
        lat=float(r.lat), lng=float(r.lng),
        contact_name=r.contact_name, contact_phone=r.contact_phone,
        services_json=r.services_json, updated_at=r.updated_at
    )
