"""
Third-party gel catalogue — DRAFT, requires manual verification.

This is a starter list of popular endurance gels sold in Switzerland (CH),
Czech Republic (CZ), and Slovakia (SK). Values are from training-data
knowledge, NOT verified against current manufacturer specs.

BEFORE RUNNING THIS:
  1. Verify carbs_g, glucose_pct, fructose_pct against each brand's website
     or the back-of-pack label.
  2. Verify availability in each market (CH/CZ/SK).
  3. Decide on size-bucket assignments — many gels don't fit cleanly into
     our small=25g / large=40g model; choose the closest bucket and note
     the discrepancy.
  4. Decide on ratio_phase assignment — many ratios don't fit cleanly into
     our phase 1 (100/0), phase 2 (67/33), phase 3 (56/44) buckets; pick
     the closest.

Run with:
    ./venv/bin/python seed_third_party.py

Idempotent: each gel is upserted by (brand, size, ratio_phase) — re-running
updates `product_name`, `carbs_g`, ratios, and `markets` so the catalogue
stays in sync with this file.
"""
from database import SessionLocal
from models_db import Gel

ALL_MARKETS = ["CH", "CZ", "SK"]


# ── PRODUCTS ────────────────────────────────────────────────────────────────
# Each dict shape: brand, product_name, size (small/large), carbs_g, glucose_pct,
# fructose_pct, ratio_phase (1/2/3), markets (list).
# product_name = the marketing-friendly name shown to athletes in the UI/PDF.
GELS = [
    # ════════════════════════════════════════════════════════════════════════
    # MAURTEN (Sweden) — hydrogel technology, widely available
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "maurten", "product_name": "Maurten Gel 100",     "size": "small", "carbs_g": 25, "glucose_pct": 56.0, "fructose_pct": 44.0, "ratio_phase": 3, "markets": ALL_MARKETS},
    {"brand": "maurten", "product_name": "Maurten Gel 160",     "size": "large", "carbs_g": 40, "glucose_pct": 56.0, "fructose_pct": 44.0, "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # SCIENCE IN SPORT — SiS (UK)
    # ════════════════════════════════════════════════════════════════════════
    # SiS Go Isotonic Energy Gel — 22g maltodextrin only (no fructose)
    # DISCREPANCY: 22g vs our 25g small bucket → overstates by ~14%
    {"brand": "sis", "product_name": "SiS Go Isotonic Energy Gel", "size": "small", "carbs_g": 22, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1, "markets": ALL_MARKETS},
    {"brand": "sis", "product_name": "SiS Beta Fuel Gel",          "size": "large", "carbs_g": 40, "glucose_pct": 56.0,  "fructose_pct": 44.0, "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # POWERBAR (Germany / international)
    # DISCREPANCY: 27g vs 25g small bucket → understates by ~7%
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "powerbar", "product_name": "PowerBar PowerGel Original", "size": "small", "carbs_g": 27, "glucose_pct": 67.0, "fructose_pct": 33.0, "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # HIGH5 (UK) — single-source carb, isotonic
    # DISCREPANCY: 23g vs 25g bucket → small overstatement
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "high5", "product_name": "High5 Energy Gel", "size": "small", "carbs_g": 23, "glucose_pct": 100.0, "fructose_pct": 0.0, "ratio_phase": 1, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # PRECISION FUEL & HYDRATION (UK) — newer brand, 1:0.8 ratio
    # ════════════════════════════════════════════════════════════════════════
    # PF 30 — 30g between small (25g) and large (40g) — using small bucket
    {"brand": "precision_fuel", "product_name": "Precision Fuel PF 30", "size": "small", "carbs_g": 30, "glucose_pct": 56.0, "fructose_pct": 44.0, "ratio_phase": 3, "markets": ALL_MARKETS},
    # PF 60 — 60g, oversized "large"; protocol treats as single large
    {"brand": "precision_fuel", "product_name": "Precision Fuel PF 60", "size": "large", "carbs_g": 60, "glucose_pct": 56.0, "fructose_pct": 44.0, "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # SPONSER (Switzerland) — Swiss brand, strong CH presence
    # DISCREPANCY: 30g vs small bucket; ratio not officially published
    # MARKETS: CH primary; CZ/SK limited (online only)
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "sponser", "product_name": "Sponser Liquid Energy Plus", "size": "small", "carbs_g": 30, "glucose_pct": 67.0, "fructose_pct": 33.0, "ratio_phase": 2, "markets": ["CH"]},

    # ════════════════════════════════════════════════════════════════════════
    # SQUEEZY (Germany)
    # DISCREPANCY: 32g closer to large (40g); ratio guessed
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "squeezy", "product_name": "Squeezy Super Energy Gel", "size": "large", "carbs_g": 32, "glucose_pct": 67.0, "fructose_pct": 33.0, "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # PENCO (Czech Republic)
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "penco", "product_name": "Penco Energy Gel",      "size": "small", "carbs_g": 30, "glucose_pct": 100.0, "fructose_pct": 0.0,  "ratio_phase": 1, "markets": ["CZ", "SK"]},
    {"brand": "penco", "product_name": "Penco Long Energy Gel", "size": "large", "carbs_g": 40, "glucose_pct": 67.0,  "fructose_pct": 33.0, "ratio_phase": 2, "markets": ["CZ", "SK"]},

    # ════════════════════════════════════════════════════════════════════════
    # GU ENERGY (USA, international)
    # DISCREPANCY: 22g vs 25g bucket
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "gu", "product_name": "GU Energy Gel", "size": "small", "carbs_g": 22, "glucose_pct": 67.0, "fructose_pct": 33.0, "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # MAXXWIN (Slovakia / Czech)
    # NEEDS VERIFICATION: brand has multiple SKUs; this is a stand-in
    # ════════════════════════════════════════════════════════════════════════
    {"brand": "maxxwin", "product_name": "Maxxwin Energy Gel", "size": "small", "carbs_g": 30, "glucose_pct": 100.0, "fructose_pct": 0.0, "ratio_phase": 1, "markets": ["CZ", "SK"]},
]


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
        print(f"Third-party gels: inserted {inserted}, updated {updated}, unchanged {unchanged}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
