from database import SessionLocal
from models_db import Gel

GELS = [
    # Phase 1 — 100% glucose
    {"size": "small", "carbs_g": 25, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1},
    {"size": "large", "carbs_g": 40, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1},
    # Phase 2 — 2:1 ratio (67% glucose / 33% fructose)
    {"size": "small", "carbs_g": 25, "glucose_pct": 67.0,  "fructose_pct": 33.0, "ratio_phase": 2},
    {"size": "large", "carbs_g": 40, "glucose_pct": 67.0,  "fructose_pct": 33.0, "ratio_phase": 2},
    # Phase 3 — 1:0.8 ratio (56% glucose / 44% fructose)
    {"size": "small", "carbs_g": 25, "glucose_pct": 56.0,  "fructose_pct": 44.0, "ratio_phase": 3},
    {"size": "large", "carbs_g": 40, "glucose_pct": 56.0,  "fructose_pct": 44.0, "ratio_phase": 3},
]

def seed():
    db = SessionLocal()
    try:
        if db.query(Gel).count() > 0:
            print("Gels already seeded, skipping.")
            return
        for g in GELS:
            db.add(Gel(**g))
        db.commit()
        print(f"Seeded {len(GELS)} gels.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
