# RuralReach

**Problem Statement ID:** CS02HA
**Team Name:** penguin.sh
**College Name:** St Aloysius Deemed to be University School Of Engineering 

---

## 1. Problem Statement

Creating an affordable health tracking system to promote regular medical check-ups, especially in rural areas.

- Who faces this problem: People living in rural and remote areas, especially elderly individuals, daily wage workers, and families with limited access to nearby healthcare facilities and medical professionals.

- Why it matters: Lack of regular health monitoring and preventive check-ups leads to late detection of diseases, higher treatment costs, and increased health risks. Many preventable or manageable conditions become severe simply because medical attention is delayed. Improving healthcare accessibility can significantly enhance quality of life and reduce avoidable medical emergencies in rural communities.

- Current gaps or limitations in existing solutions
    - No offline-first design: Many systems assume stable internet, but rural areas often face weak connectivity, making real-time apps unreliable during camps.
    - Poor follow-up tracking: Screening happens once, but follow-up reminders and task closures are inconsistent, causing missed rechecks and drop-offs.
    - Lack of accountability in field data: Vital entries can be fabricated or entered later without proof of patient presence, reducing trust in screening data.
    - Location confusion for camps: People miss checkups because they don’t know exactly where and when camps are being conducted.
    - Fragmented records: Household-level tracking and longitudinal trends are often missing, making it hard to prioritize high-risk individuals.

---

## 2. Proposed Solution

RuralReach is an offline-first health tracking platform designed for rural clinics and medical camps. It enables village-wide health registration, fast screening workflows, triage-based prioritization, and structured follow-ups—while remaining reliable under low connectivity.

What the system does:
- Maintains a village health registry (households + individuals)
- Allows medical workers to run camp/clinic checkups and record vitals + point-of-care tests
- Automatically generates:
    - Triage (Green / Amber / Red)
    - Health score (explainable domain-based)
    - Next checkup due date and follow-up requirement
- Provides task + reminder workflows so no patient is lost after screening
- Publishes camp locations with Google Maps coordinates so patients know where to go

### How it solves the stated problem:
- Makes screenings feasible even in bad internet by working offline and syncing later
- Turns one-time checkups into a repeatable preventive cycle with follow-ups and reminders
- Improves data trust using patient presence verification
- Improves attendance by giving patients clear camp location + timings + contact

Triage + scoring + due engine

Automatically categorizes patients:
- Red: urgent referral
- Amber: follow-up soon
- Green: routine recheck

Computes an explainable health score using domain scores (cardiometabolic, respiratory, etc.)

Generates “Next checkup due” date + reason

### Why this approach is effective?
- It is designed around real rural constraints: low connectivity, limited devices, time pressure at camps
- Converts screening into a structured pipeline: screen → triage → task → reminder → follow-up
- Builds trust and auditability through verified encounters and role-based accountability

---

## 3. Innovation & Creativity

RuralReach combines public-health workflow thinking with a trust & accountability layer suitable for rural camps.

### Novel aspects
- Presence-Verified Screening (TOTP):
Each checkup can be validated as “patient-present” using a 6-digit rotating code, reducing fabricated encounters.
- Due Engine for Regular Checkups:
Not just “record vitals once,” but automatically computes when the next checkup is required and why.
- Offline-first with guaranteed capture:
Workers can complete checkups even with zero internet—data syncs later without loss.
- Household-first design:
Rural health works best at family level. Healthify tracks households and members together for better outreach.
- Camp navigation for rural attendance:
Coordinates + address + landmark + contact reduce missed visits due to location confusion.

Include:
- Novel aspects of the solution
- How it is different from existing solutions
- Any creative or original thinking involved

### How it differs from common solutions?
Most tracking systems focus on digitizing records but fail in rural connectivity and follow-up cycles. RuralReach specifically focuses on:
- offline-first operation,
- verified encounters,
- and a “repeat checkup” loop driven by tasks + reminders.

---

## 4. Technical Complexity & Stack

List all tools, frameworks, languages, and platforms used.

**Frontend:**
- HTML, CSS, Vanilla JavaScript
- PWA (Service Worker + Manifest)
- IndexedDB (offline local cache + outbox queue)


**Backend:**
- Python (FastAPI)
- JWT Authentication + RBAC
- TOTP verification logic (RFC 6238)


**Database:**
- PostgreSQL
- Alembic migrations


**APIs / Libraries:**
- `pyotp` (TOTP verification)
- Fetch API for network calls

**Other Tools / Platforms:**  
- Uvicorn (ASGI server)
- Capacitor (future plan to wrap PWA into Android/iOS app)

### Why these were chosen?
- FastAPI + SQLAlchemy for fast iteration and clean API design
- PostgreSQL for reliable relational storage and data integrity
- PWA + IndexedDB for offline-first behavior in rural connectivity
- TOTP for lightweight, time-based presence verification
---

## 5. Usability & Impact

**Target users:**
- Field enumerators
- Screening staff
- Clinicians
- Admins/program managers
- Patients (viewing codes and camp info)

**User flow:**
1. Admin creates camps and staff accounts
2. Enumerator registers households and people
3. Screener starts encounter, records vitals/tests
4. TOTP presence is verified (online) or marked unverified (offline)
5. Clinician reviews and approves/rejects unverified encounters
6. Tasks and reminders ensure follow-up completion

**Expected benefits:**
- Higher screening coverage with lower drop-off
- Faster identification of high-risk patients
- Reliable data capture even offline
- Stronger auditability and accountability

**Scalability / future potential:**
- Integrate with public health registries
- Expand to chronic condition programs (diabetes, HTN, COPD)
- Add SMS reminders and multilingual patient messages

---

## 6. Setup Instructions

Postgresql setup:
```
1. Open SQL Shell (psql)

2. CREATE USER rh_user WITH PASSWORD 'rh_pass';

3. CREATE DATABASE rural_health OWNER rh_user;

4. GRANT ALL PRIVILEGES ON DATABASE rural_health TO rh_user;

5. ALTER ROLE rh_user CREATEDB;

6. \q

7. Start the service.
```

### Terminal 1:

```
git clone https://github.com/aaronkennyz/codesprint-penguinsh

cd backend

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

alembic upgrade head

python -m app.scripts.seed_demo

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 (still venv):


```
cd ..\frontend

python -m http.server 5173


### Open in browser:

http://127.0.0.1:5173/login.html

```