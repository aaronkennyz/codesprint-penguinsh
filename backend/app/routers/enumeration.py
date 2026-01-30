from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from ..db import get_db
from ..models import Household, Person
from ..schemas import HouseholdIn, HouseholdOut, PersonIn, PersonOut
from ..security import require_perm

router = APIRouter(prefix="/api", tags=["enumeration"])

@router.post("/households", response_model=HouseholdOut, dependencies=[Depends(require_perm("household:create"))])
def create_household(body: HouseholdIn, db: Session = Depends(get_db)):
    h = Household(**body.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return HouseholdOut(**body.model_dump(), id=h.id, updated_at=h.updated_at)

@router.get("/households", response_model=list[HouseholdOut], dependencies=[Depends(require_perm("due:view_assigned"))])
def list_households(village_id: int, updated_since: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Household).filter(Household.village_id == village_id)
    if updated_since:
        dt = datetime.fromisoformat(updated_since)
        q = q.filter(Household.updated_at > dt)
    rows = q.order_by(Household.updated_at.asc()).limit(500).all()
    return [HouseholdOut(
        id=r.id, village_id=r.village_id, hamlet=r.hamlet, address=r.address,
        head_name=r.head_name, phone=r.phone, updated_at=r.updated_at
    ) for r in rows]

@router.post("/people", response_model=PersonOut, dependencies=[Depends(require_perm("people:create"))])
def create_person(body: PersonIn, db: Session = Depends(get_db)):
    p = Person(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return PersonOut(**body.model_dump(), id=p.id, updated_at=p.updated_at)

@router.get("/people", response_model=list[PersonOut], dependencies=[Depends(require_perm("due:view_assigned"))])
def list_people(search: str = "", village_id: int | None = None, updated_since: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Person)
    if village_id:
        q = q.filter(Person.village_id == village_id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Person.full_name.ilike(like), Person.phone.ilike(like)))
    if updated_since:
        dt = datetime.fromisoformat(updated_since)
        q = q.filter(Person.updated_at > dt)
    rows = q.order_by(Person.updated_at.asc()).limit(500).all()
    return [PersonOut(
        id=r.id, household_id=r.household_id, village_id=r.village_id,
        full_name=r.full_name, sex=r.sex, dob=r.dob, phone=r.phone,
        demographics_json=r.demographics_json, risk_survey_json=r.risk_survey_json,
        updated_at=r.updated_at
    ) for r in rows]
