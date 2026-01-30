from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db import SessionLocal
from app.models import Village, Household, Person, Worker, Camp
from app.security import hash_password
from app.rbac import Role

def run():
    db: Session = SessionLocal()
    try:
        v1 = Village(name="Kallur", district="Demo", state="KA")
        v2 = Village(name="Hosanagar", district="Demo", state="KA")
        db.add_all([v1, v2]); db.commit()
        db.refresh(v1); db.refresh(v2)

        enum = Worker(username="enum1", password_hash=hash_password("enum1"), role=Role.ENUMERATOR.value, display_name="Enumerator 1", assigned_villages_json=[v1.id])
        scr = Worker(username="screen1", password_hash=hash_password("screen1"), role=Role.SCREENER.value, display_name="Screener 1", assigned_villages_json=[v1.id])
        clin = Worker(username="clin1", password_hash=hash_password("clin1"), role=Role.CLINICIAN.value, display_name="Clinician 1")
        admin = Worker(username="admin1", password_hash=hash_password("admin1"), role=Role.ADMIN.value, display_name="Admin 1")

        db.add_all([enum, scr, clin, admin]); db.commit()

        hh = Household(village_id=v1.id, hamlet="Main", head_name="Ravi", phone="9000000000", address="Near school")
        db.add(hh); db.commit(); db.refresh(hh)

        p1 = Person(household_id=hh.id, village_id=v1.id, full_name="Sita Devi", sex="F", phone="9000000001")
        p2 = Person(household_id=hh.id, village_id=v1.id, full_name="Ravi Kumar", sex="M", phone="9000000002")
        db.add_all([p1, p2]); db.commit(); db.refresh(p1); db.refresh(p2)

        c1 = Camp(
            village_id=v1.id, name="NCD Screening Camp",
            date=date.today() + timedelta(days=2),
            start_time="10:00", end_time="14:00",
            address="Govt School Ground", landmark="Water tank",
            lat=12.9716000, lng=77.5946000,
            contact_name="ASHA Latha", contact_phone="9000000099",
            services_json={"bp": True, "glucose": True, "spo2": True},
        )
        db.add(c1); db.commit()

        print("Seeded demo data.")
        print("Workers: enum1/enum1, screen1/screen1, clin1/clin1, admin1/admin1")
        print("Patient demo login: username=<person_id>, password=<phone_last4> (e.g., 1 / 0001)")
    finally:
        db.close()

if __name__ == "__main__":
    run()
