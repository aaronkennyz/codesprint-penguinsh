import base64, secrets
from datetime import datetime, timedelta, timezone
import pyotp
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db import get_db
from ..config import settings
from ..models import Person, TotpSecret, VerificationToken, Encounter
from ..schemas import TotpInitOut, VerifyTotpIn, VerifyTotpOut
from ..security import require_perm
from ..rbac import Role

router = APIRouter(prefix="/api", tags=["totp"])
fernet = Fernet(settings.FERNET_KEY.encode() if isinstance(settings.FERNET_KEY, str) else settings.FERNET_KEY)

def _decrypt_secret(ts: TotpSecret) -> str:
    return fernet.decrypt(ts.secret_encrypted).decode()

def _encrypt_secret(secret: str) -> bytes:
    return fernet.encrypt(secret.encode())

@router.post("/people/{person_id}/totp/init", response_model=TotpInitOut, dependencies=[Depends(require_perm("admin:manage"))])
def init_totp(person_id: int, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(404, "Person not found")

    ts = db.get(TotpSecret, person_id)
    if not ts:
        secret = pyotp.random_base32()
        ts = TotpSecret(person_id=person_id, secret_encrypted=_encrypt_secret(secret), provisioning_done=True)
        db.add(ts)
        db.commit()
    else:
        secret = _decrypt_secret(ts)
        ts.provisioning_done = True
        db.commit()

    totp = pyotp.TOTP(secret, interval=30)
    issuer = settings.APP_NAME
    name = f"person-{person_id}"
    uri = totp.provisioning_uri(name=name, issuer_name=issuer)

    # Patient QR requirement in spec: patient QR encodes ONLY the 6 digits (changes every 30s).
    # For provisioning, we still return otpauth URI (admin flow).
    return TotpInitOut(provisioning_uri=uri, otpauth_qr_data=uri)

@router.post("/verify-totp", response_model=VerifyTotpOut, dependencies=[Depends(require_perm("encounter:submit"))])
def verify_totp(body: VerifyTotpIn, db: Session = Depends(get_db)):
    p = db.get(Person, body.person_id)
    if not p:
        raise HTTPException(404, "Person not found")
    enc = db.get(Encounter, body.encounter_id)
    if not enc or enc.person_id != body.person_id:
        raise HTTPException(400, "Invalid encounter")

    ts = db.get(TotpSecret, body.person_id)
    if not ts:
        raise HTTPException(400, "TOTP not provisioned")

    secret = _decrypt_secret(ts)
    totp = pyotp.TOTP(secret, interval=30)

    # ±1 timestep drift
    now = datetime.now(timezone.utc)
    timestep = int(now.timestamp()) // 30
    ok = totp.verify(body.code, valid_window=1)
    if not ok:
        raise HTTPException(400, "Invalid code")

    # anti-replay via timestep
    if timestep <= (ts.last_verified_timestep or 0):
        raise HTTPException(409, "Replay detected")
    ts.last_verified_timestep = timestep
    db.add(ts)

    token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(minutes=2)
    vt = VerificationToken(encounter_id=body.encounter_id, token=token, expires_at=expires_at, used=False)
    db.add(vt)
    db.commit()

    return VerifyTotpOut(verification_token=token, expires_at=expires_at)
