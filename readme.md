# Healthify

**Problem Statement ID:** CS02HA
**Team Name:** penguin.sh
**College Name:** St Aloysius Deemed to be University School Of Engineering 

---

## 1. Problem Statement

Creating an affordable health tracking system to promote regular medical check-ups, especially in rural areas.

- Who faces this problem: People living in rural and remote areas, especially elderly individuals, daily wage workers, and families with limited access to nearby healthcare facilities and medical professionals.

- Why it matters: Lack of regular health monitoring and preventive check-ups leads to late detection of diseases, higher treatment costs, and increased health risks. Many preventable or manageable conditions become severe simply because medical attention is delayed. Improving healthcare accessibility can significantly enhance quality of life and reduce avoidable medical emergencies in rural communities.

- Current gaps or limitations in existing solutions

---

## 2. Proposed Solution

Explain your solution clearly.

Include:
- What your system does
- How it solves the stated problem
- Key features and workflow
- Why this approach is effective

---

## 3. Innovation & Creativity

Describe what makes your idea unique.

Include:
- Novel aspects of the solution
- How it is different from existing solutions
- Any creative or original thinking involved

---

## 4. Technical Complexity & Stack

List all tools, frameworks, languages, and platforms used.

**Frontend:**  
**Backend:**  
**Database:**  
**APIs / Libraries:**  
**Other Tools / Platforms:**  

Briefly explain why these technologies were chosen.

---

## 5. Usability & Impact

Explain how users interact with your solution and its real-world impact.

Include:
- Target users
- User flow (how users use the system)
- Expected benefits and outcomes
- Scalability or future potential (if any)

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

cd ..\frontend

python -m http.server 5173
```

### Open in browser:

http://127.0.0.1:5173/login.html