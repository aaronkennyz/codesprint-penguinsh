from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Worker, Person
from ..schemas import LoginIn, LoginOut, MeOut
from ..security import verify_password, create_access_token, get_principal
from ..rbac import Role

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    w = db.query(Worker).filter(Worker.username == body.username, Worker.is_active == True).first()
    if w and verify_password(body.password, w.password_hash):
        token = create_access_token(subject=w.username, role=w.role, worker_id=w.id, person_id=None)
        return LoginOut(access_token=token, role=w.role, worker_id=w.id)

    # Optional: patient login (simple demo: username = person_id, password = phone last4)
    if body.username.isdigit():
        p = db.get(Person, int(body.username))
        if p and p.phone and p.phone[-4:] == body.password:
            token = create_access_token(subject=f"person:{p.id}", role=Role.PATIENT.value, worker_id=None, person_id=p.id)
            return LoginOut(access_token=token, role=Role.PATIENT.value, person_id=p.id)

    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/me", response_model=MeOut)
def me(pr = Depends(get_principal)):
    if pr.worker:
        assigned = pr.worker.assigned_villages_json or []
        return MeOut(role=pr.role.value, worker_id=pr.worker.id, display_name=pr.worker.display_name, assigned_villages=assigned)
    if pr.person:
        return MeOut(role=pr.role.value, person_id=pr.person.id, display_name=pr.person.full_name, assigned_villages=[])
    return MeOut(role=pr.role.value)
