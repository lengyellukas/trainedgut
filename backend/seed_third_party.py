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

Idempotent: each gel is only inserted if a (brand, size, ratio_phase) row
with that combination does not already exist.
"""
from database import SessionLocal
from models_db import Gel

ALL_MARKETS = ["CH", "CZ", "SK"]


# ── PRODUCTS ────────────────────────────────────────────────────────────────
# Each dict shape: brand, size (small/large), carbs_g, glucose_pct,
# fructose_pct, ratio_phase (1/2/3), markets (list).
# Comments above each block: product name + source notes + known discrepancies.
GELS = [
    # ════════════════════════════════════════════════════════════════════════
    # MAURTEN (Sweden) — hydrogel technology, widely available
    # ════════════════════════════════════════════════════════════════════════

    # Maurten Gel 100 — 25g maltodextrin + fructose, ratio published as ~0.8:1
    # CLOSEST FIT: size=small (exact), phase=3 (closest to 1:0.8)
    {"brand": "maurten", "size": "small", "carbs_g": 25, "glucose_pct": 56.0, "fructose_pct": 44.0,
     "ratio_phase": 3, "markets": ALL_MARKETS},

    # Maurten Gel 160 — 40g, same composition as Gel 100
    # CLOSEST FIT: size=large (exact), phase=3
    {"brand": "maurten", "size": "large", "carbs_g": 40, "glucose_pct": 56.0, "fructose_pct": 44.0,
     "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # SCIENCE IN SPORT — SiS (UK), widely available across Europe
    # ════════════════════════════════════════════════════════════════════════

    # SiS Go Isotonic Energy Gel — 22g maltodextrin only (no fructose)
    # DISCREPANCY: 22g vs our 25g small bucket → overstates carbs by ~14% if used
    {"brand": "sis", "size": "small", "carbs_g": 22, "glucose_pct": 100.0, "fructose_pct": 0.0,
     "ratio_phase": 1, "markets": ALL_MARKETS},

    # SiS Beta Fuel Gel — 40g, 1:0.8 maltodextrin:fructose
    # CLOSEST FIT: size=large (exact), phase=3 (exact)
    {"brand": "sis", "size": "large", "carbs_g": 40, "glucose_pct": 56.0, "fructose_pct": 44.0,
     "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # POWERBAR (Germany / international)
    # ════════════════════════════════════════════════════════════════════════

    # PowerBar PowerGel Original — 27g, maltodextrin + fructose, ~2:1
    # DISCREPANCY: 27g vs 25g small bucket → understates carbs by ~7%
    {"brand": "powerbar", "size": "small", "carbs_g": 27, "glucose_pct": 67.0, "fructose_pct": 33.0,
     "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # HIGH5 (UK) — single-source carb, isotonic
    # ════════════════════════════════════════════════════════════════════════

    # High5 Energy Gel — 23g maltodextrin only
    # DISCREPANCY: 23g vs 25g bucket → small overstatement
    {"brand": "high5", "size": "small", "carbs_g": 23, "glucose_pct": 100.0, "fructose_pct": 0.0,
     "ratio_phase": 1, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # PRECISION FUEL & HYDRATION (UK) — newer brand, 1:0.8 ratio
    # ════════════════════════════════════════════════════════════════════════

    # PF 30 — 30g maltodextrin:fructose 1:0.8
    # DISCREPANCY: 30g falls between small (25g) and large (40g); using small
    # is a fit gap — really wants its own "medium" bucket
    {"brand": "precision_fuel", "size": "small", "carbs_g": 30, "glucose_pct": 56.0, "fructose_pct": 44.0,
     "ratio_phase": 3, "markets": ALL_MARKETS},

    # PF 60 — 60g maltodextrin:fructose 1:0.8 (oversized "large")
    # DISCREPANCY: 60g exceeds our 40g large bucket; protocol would treat as
    # a single large and understate carbs by 33%
    {"brand": "precision_fuel", "size": "large", "carbs_g": 60, "glucose_pct": 56.0, "fructose_pct": 44.0,
     "ratio_phase": 3, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # SPONSER (Switzerland) — Swiss brand, strong CH presence
    # ════════════════════════════════════════════════════════════════════════

    # Sponser Liquid Energy Plus — ~30g, maltodextrin + fructose, sodium added
    # DISCREPANCY: 30g vs small bucket; ratio not officially published
    # MARKETS: CH primary; CZ/SK limited (online only)
    {"brand": "sponser", "size": "small", "carbs_g": 30, "glucose_pct": 67.0, "fructose_pct": 33.0,
     "ratio_phase": 2, "markets": ["CH"]},

    # ════════════════════════════════════════════════════════════════════════
    # SQUEEZY (Germany) — multi-source, popular in DACH + CZ/SK
    # ════════════════════════════════════════════════════════════════════════

    # Squeezy Super Energy Gel — 32g, maltodextrin + fructose
    # DISCREPANCY: 32g closer to large (40g) than small (25g); ratio guessed
    {"brand": "squeezy", "size": "large", "carbs_g": 32, "glucose_pct": 67.0, "fructose_pct": 33.0,
     "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # PENCO (Czech Republic) — Czech brand, strong CZ/SK presence
    # ════════════════════════════════════════════════════════════════════════

    # Penco Energy Gel — ~30g maltodextrin (some variants with fructose)
    # DISCREPANCY: 30g vs small; phase assignment depends on variant
    {"brand": "penco", "size": "small", "carbs_g": 30, "glucose_pct": 100.0, "fructose_pct": 0.0,
     "ratio_phase": 1, "markets": ["CZ", "SK"]},

    # Penco Long Energy Gel — endurance variant, multi-source carbs
    # GUESSED: ~40g, multi-source 2:1 (verify on Penco site)
    {"brand": "penco", "size": "large", "carbs_g": 40, "glucose_pct": 67.0, "fructose_pct": 33.0,
     "ratio_phase": 2, "markets": ["CZ", "SK"]},

    # ════════════════════════════════════════════════════════════════════════
    # GU ENERGY (USA, international) — 22g, multi-source
    # ════════════════════════════════════════════════════════════════════════

    # GU Energy Gel — 22g maltodextrin + fructose
    # DISCREPANCY: 22g vs 25g bucket
    {"brand": "gu", "size": "small", "carbs_g": 22, "glucose_pct": 67.0, "fructose_pct": 33.0,
     "ratio_phase": 2, "markets": ALL_MARKETS},

    # ════════════════════════════════════════════════════════════════════════
    # MAXXWIN (Slovakia / Czech) — local CZ/SK brand
    # ════════════════════════════════════════════════════════════════════════

    # Maxxwin Energy Gel — ~30g, composition varies by product line
    # NEEDS VERIFICATION: brand has multiple gel SKUs; this is a stand-in
    {"brand": "maxxwin", "size": "small", "carbs_g": 30, "glucose_pct": 100.0, "fructose_pct": 0.0,
     "ratio_phase": 1, "markets": ["CZ", "SK"]},
]


def seed():
    db = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        for g in GELS:
            existing = (
                db.query(Gel)
                .filter(Gel.brand == g["brand"], Gel.size == g["size"], Gel.ratio_phase == g["ratio_phase"])
                .first()
            )
            if existing:
                skipped += 1
                continue
            db.add(Gel(**g))
            inserted += 1
        db.commit()
        print(f"Third-party gels: inserted {inserted}, skipped {skipped} (already present).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
