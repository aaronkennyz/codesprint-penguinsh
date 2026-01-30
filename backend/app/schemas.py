from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import date, datetime

class LoginIn(BaseModel):
    username: str
    password: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    worker_id: int | None = None
    person_id: int | None = None

class MeOut(BaseModel):
    role: str
    worker_id: int | None = None
    person_id: int | None = None
    display_name: str | None = None
    assigned_villages: list[int] = []

class HouseholdIn(BaseModel):
    village_id: int
    hamlet: Optional[str] = None
    address: Optional[str] = None
    head_name: Optional[str] = None
    phone: Optional[str] = None

class HouseholdOut(HouseholdIn):
    id: int
    updated_at: datetime

class PersonIn(BaseModel):
    household_id: int
    village_id: int
    full_name: str
    sex: Optional[str] = None
    dob: Optional[date] = None
    phone: Optional[str] = None
    demographics_json: Optional[Dict[str, Any]] = None
    risk_survey_json: Optional[Dict[str, Any]] = None

class PersonOut(PersonIn):
    id: int
    updated_at: datetime

class CampIn(BaseModel):
    village_id: int
    name: str
    date: date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    lat: float
    lng: float
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    services_json: Optional[Dict[str, Any]] = None

class CampOut(CampIn):
    id: int
    updated_at: datetime

class WorkerCreateIn(BaseModel):
    username: str
    password: str
    role: str
    display_name: str | None = None
    phone: str | None = None
    assigned_villages: list[int] | None = None

class WorkerOut(BaseModel):
    id: int
    username: str
    role: str
    display_name: str | None = None
    phone: str | None = None
    assigned_villages: list[int] | None = None
    is_active: bool
    updated_at: datetime

class TotpInitOut(BaseModel):
    provisioning_uri: str
    otpauth_qr_data: str

class VerifyTotpIn(BaseModel):
    person_id: int
    encounter_id: int
    code: str = Field(min_length=6, max_length=6)
    client_time: Optional[str] = None

class VerifyTotpOut(BaseModel):
    verification_token: str
    expires_at: datetime

class EncounterStartIn(BaseModel):
    person_id: int
    camp_id: Optional[int] = None
    client_created_at: Optional[datetime] = None

class EncounterStartOut(BaseModel):
    encounter_id: int
    status: str

class VitalsIn(BaseModel):
    sbp1: Optional[int] = None
    dbp1: Optional[int] = None
    sbp2: Optional[int] = None
    dbp2: Optional[int] = None
    hr: Optional[int] = None
    spo2: Optional[int] = None
    temp: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    waist: Optional[float] = None
    symptoms_json: Optional[Dict[str, Any]] = None
    risk_json: Optional[Dict[str, Any]] = None
    consent: bool = True

class TestsIn(BaseModel):
    glucose_type: Optional[str] = None
    glucose_value: Optional[int] = None
    hb: Optional[float] = None
    urine_dip_json: Optional[Dict[str, Any]] = None

class EncounterSubmitIn(BaseModel):
    vitals: VitalsIn
    tests: TestsIn
    rules_version: str
    derived: Dict[str, Any]  # computed on client offline
    verification_token: Optional[str] = None  # if VERIFIED online flow; else missing => UNVERIFIED
    client_submitted_at: Optional[datetime] = None

class EncounterSubmitOut(BaseModel):
    status: str
    rag: str
    overall_score: Optional[int] = None

class QueueItem(BaseModel):
    encounter_id: int
    person_id: int
    person_name: str
    rag: str
    status: str
    submitted_at: Optional[datetime] = None

class TaskIn(BaseModel):
    person_id: int
    encounter_id: Optional[int] = None
    type: str
    due_date: Optional[date] = None
    notes: Optional[str] = None

class TaskOut(TaskIn):
    id: int
    status: str

class ReminderIn(BaseModel):
    person_id: int
    outcome: str
    notes: Optional[str] = None
