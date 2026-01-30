from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text,
    Numeric, JSON, LargeBinary, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .db import Base

class Village(Base):
    __tablename__ = "villages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(120), nullable=True)
    state: Mapped[str] = mapped_column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Household(Base):
    __tablename__ = "households"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    village_id: Mapped[int] = mapped_column(ForeignKey("villages.id"), nullable=False)
    hamlet: Mapped[str] = mapped_column(String(120), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    head_name: Mapped[str] = mapped_column(String(120), nullable=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    village = relationship("Village")

class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), nullable=False)
    village_id: Mapped[int] = mapped_column(ForeignKey("villages.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    sex: Mapped[str] = mapped_column(String(16), nullable=True)
    dob: Mapped[Date] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    demographics_json = Column(JSON, nullable=True)  # extra fields (occupation, etc)
    risk_survey_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    household = relationship("Household")

class Worker(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    assigned_villages_json = Column(JSON, nullable=True)  # list of village ids
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Camp(Base):
    __tablename__ = "camps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    village_id: Mapped[int] = mapped_column(ForeignKey("villages.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(String(16), nullable=True)
    end_time: Mapped[str] = mapped_column(String(16), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    landmark: Mapped[str] = mapped_column(String(160), nullable=True)
    lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(120), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(32), nullable=True)
    services_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    village = relationship("Village")

class TotpSecret(Base):
    __tablename__ = "totp_secrets"
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    secret_encrypted = Column(LargeBinary, nullable=False)
    provisioning_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_verified_timestep: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Encounter(Base):
    __tablename__ = "encounters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    camp_id: Mapped[int] = mapped_column(ForeignKey("camps.id"), nullable=True)
    started_by_worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # DRAFT/VERIFIED/UNVERIFIED
    verified_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    client_created_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Vitals(Base):
    __tablename__ = "vitals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), unique=True, nullable=False)
    sbp1 = Column(Integer, nullable=True)
    dbp1 = Column(Integer, nullable=True)
    sbp2 = Column(Integer, nullable=True)
    dbp2 = Column(Integer, nullable=True)
    sbp_avg = Column(Integer, nullable=True)
    dbp_avg = Column(Integer, nullable=True)
    hr = Column(Integer, nullable=True)
    spo2 = Column(Integer, nullable=True)
    temp = Column(Numeric(4, 1), nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    height = Column(Numeric(4, 2), nullable=True)
    bmi = Column(Numeric(5, 2), nullable=True)
    waist = Column(Numeric(6, 2), nullable=True)
    symptoms_json = Column(JSON, nullable=True)
    risk_json = Column(JSON, nullable=True)
    consent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Tests(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), unique=True, nullable=False)
    glucose_type = Column(String(16), nullable=True)  # FASTING/RANDOM
    glucose_value = Column(Integer, nullable=True)
    hb = Column(Numeric(4, 1), nullable=True)
    urine_dip_json = Column(JSON, nullable=True)

class DerivedResult(Base):
    __tablename__ = "derived_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), unique=True, nullable=False)
    rag = Column(String(8), nullable=False)
    flags_json = Column(JSON, nullable=True)
    next_step = Column(Text, nullable=True)
    followup_date = Column(Date, nullable=True)
    domain_scores_json = Column(JSON, nullable=True)
    overall_score = Column(Integer, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), nullable=True)
    type = Column(String(32), nullable=False)  # follow-up/referral
    status = Column(String(16), nullable=False)  # OPEN/CLOSED
    due_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_by_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    closed_by_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ReminderLog(Base):
    __tablename__ = "reminder_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    outcome = Column(String(32), nullable=False)  # reached/not_reached/visited/declined
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    unit = Column(String(32), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    meta_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    actor_person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    action = Column(String(64), nullable=False)
    entity = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=True)
    meta_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

Index("ix_people_village_updated", Person.village_id, Person.updated_at)
Index("ix_households_village_updated", Household.village_id, Household.updated_at)
Index("ix_camps_village_date", Camp.village_id, Camp.date)
