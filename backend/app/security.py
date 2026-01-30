from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import Worker, Person
from .rbac import Role, has_perm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/login")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(subject: str, role: str, worker_id: int | None, person_id: int | None):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    payload = {"sub": subject, "role": role, "worker_id": worker_id, "person_id": person_id, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

class Principal:
    def __init__(self, role: Role, worker: Worker | None, person: Person | None):
        self.role = role
        self.worker = worker
        self.person = person

def get_principal(db: Session = Depends(get_db), token: str = Depends(oauth2)) -> Principal:
    payload = decode_token(token)
    role = Role(payload.get("role"))
    worker_id = payload.get("worker_id")
    person_id = payload.get("person_id")

    worker = db.get(Worker, worker_id) if worker_id else None
    person = db.get(Person, person_id) if person_id else None
    return Principal(role, worker, person)

def require_perm(perm: str):
    def dep(p: Principal = Depends(get_principal)):
        if not has_perm(p.role, perm):
            raise HTTPException(status_code=403, detail="Forbidden")
        return p
    return dep
