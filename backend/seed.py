from database import SessionLocal
from models_db import Gel

TRAINEDGUT_MARKETS = ["CH", "CZ", "SK"]

# Upsert source-of-truth for TrainedGut's own gel catalogue. The product_name
# is what the athlete will see in the app + PDF + email — keep it athlete-facing.
GELS = [
    # Phase 1 — 100% glucose
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 1 - Small (Glucose)", "markets": TRAINEDGUT_MARKETS, "size": "small", "carbs_g": 25, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1},
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 1 - Large (Glucose)", "markets": TRAINEDGUT_MARKETS, "size": "large", "carbs_g": 40, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1},
    # Phase 2 — 2:1 ratio (67% glucose / 33% fructose)
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 2 - Small (2:1)",     "markets": TRAINEDGUT_MARKETS, "size": "small", "carbs_g": 25, "glucose_pct": 67.0,  "fructose_pct": 33.0, "ratio_phase": 2},
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 2 - Large (2:1)",     "markets": TRAINEDGUT_MARKETS, "size": "large", "carbs_g": 40, "glucose_pct": 67.0,  "fructose_pct": 33.0, "ratio_phase": 2},
    # Phase 3 — 1:0.8 ratio (56% glucose / 44% fructose)
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 3 - Small (1:0.8)",   "markets": TRAINEDGUT_MARKETS, "size": "small", "carbs_g": 25, "glucose_pct": 56.0,  "fructose_pct": 44.0, "ratio_phase": 3},
    {"brand": "trainedgut", "product_name": "TrainedGut Phase 3 - Large (1:0.8)",   "markets": TRAINEDGUT_MARKETS, "size": "large", "carbs_g": 40, "glucose_pct": 56.0,  "fructose_pct": 44.0, "ratio_phase": 3},
]


# Fields that get refreshed on re-seed if they drift from the source-of-truth above.
_UPDATABLE_FIELDS = ["product_name", "carbs_g", "glucose_pct", "fructose_pct", "markets"]


def seed():
    db = SessionLocal()
    inserted = updated = unchanged = 0
    try:
        for g in GELS:
            existing = (
                db.query(Gel)
                .filter(Gel.brand == g["brand"], Gel.size == g["size"], Gel.ratio_phase == g["ratio_phase"])
                .first()
            )
            if existing:
                changed = False
                for field in _UPDATABLE_FIELDS:
                    if field in g and getattr(existing, field, None) != g[field]:
                        setattr(existing, field, g[field])
                        changed = True
                if changed:
                    updated += 1
                else:
                    unchanged += 1
                continue
            db.add(Gel(**g))
            inserted += 1
        db.commit()
        print(f"TrainedGut gels: inserted {inserted}, updated {updated}, unchanged {unchanged}.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
