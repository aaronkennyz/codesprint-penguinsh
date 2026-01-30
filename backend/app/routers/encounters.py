from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db import get_db
from ..models import Encounter, Vitals, Tests, DerivedResult, VerificationToken
from ..schemas import EncounterStartIn, EncounterStartOut, EncounterSubmitIn, EncounterSubmitOut
from ..security import require_perm, get_principal
from ..triage import compute_bp_avg, compute_bmi

router = APIRouter(prefix="/api", tags=["encounters"])

@router.post("/encounters/start", response_model=EncounterStartOut, dependencies=[Depends(require_perm("encounter:start"))])
def start_encounter(body: EncounterStartIn, db: Session = Depends(get_db), pr=Depends(get_principal)):
    if not pr.worker:
        raise HTTPException(403, "Worker required")
    enc = Encounter(
        person_id=body.person_id,
        camp_id=body.camp_id,
        started_by_worker_id=pr.worker.id,
        status="DRAFT",
        client_created_at=body.client_created_at,
    )
    db.add(enc)
    db.commit()
    db.refresh(enc)
    return EncounterStartOut(encounter_id=enc.id, status=enc.status)

@router.post("/encounters/{encounter_id}/submit", response_model=EncounterSubmitOut, dependencies=[Depends(require_perm("encounter:submit"))])
def submit_encounter(encounter_id: int, body: EncounterSubmitIn, db: Session = Depends(get_db), pr=Depends(get_principal)):
    enc = db.get(Encounter, encounter_id)
    if not enc:
        raise HTTPException(404, "Encounter not found")
    if enc.status != "DRAFT":
        raise HTTPException(409, "Encounter already submitted")

    # Verify token if provided (online verified path)
    status = "UNVERIFIED"
    if body.verification_token:
        vt = db.query(VerificationToken).filter(
            VerificationToken.token == body.verification_token,
            VerificationToken.encounter_id == encounter_id,
            VerificationToken.used == False
        ).first()
        if not vt:
            raise HTTPException(400, "Invalid verification token")
        now = datetime.now(timezone.utc)
        if vt.expires_at < now:
            raise HTTPException(400, "Verification token expired")
        vt.used = True
        status = "VERIFIED"
        enc.verified_at = now

    enc.status = status
    enc.submitted_at = datetime.now(timezone.utc)

    # Store vitals/tests (compute avg/bmi server-side)
    v = Vitals(encounter_id=encounter_id, **body.vitals.model_dump())
    sbp_avg, dbp_avg = compute_bp_avg(v.sbp1, v.dbp1, v.sbp2, v.dbp2)
    v.sbp_avg = sbp_avg
    v.dbp_avg = dbp_avg
    v.bmi = compute_bmi(float(v.weight) if v.weight else None, float(v.height) if v.height else None)

    t = Tests(encounter_id=encounter_id, **body.tests.model_dump())

    # Save derived results from client rules engine (offline-first)
    derived = body.derived or {}
    dr = DerivedResult(
        encounter_id=encounter_id,
        rag=derived.get("rag", "GREEN"),
        flags_json=derived.get("flags", []),
        next_step=derived.get("next_step"),
        followup_date=derived.get("next_due_date"),
        domain_scores_json=derived.get("domain_scores"),
        overall_score=derived.get("overall_score"),
    )

    db.add(v); db.add(t); db.add(dr); db.add(enc)
    db.commit()

    return EncounterSubmitOut(status=enc.status, rag=dr.rag, overall_score=dr.overall_score)
