# ── Research-backed constants ─────────────────────────────────────────────────
# Do not change these without a peer-reviewed source.

# Source: Styrkr gut training review
MIN_STARTING_CARBS_G_PER_HOUR = 30

# Source: Jeukendrup 2008
STANDARD_CARB_CEILING_G_PER_HOUR = 90

# Source: ScienceDirect 2026 review
ELITE_CARB_CEILING_G_PER_HOUR = 120

# Product logic — threshold at which elite ceiling unlocks; validate with nutritionist
ELITE_UNLOCK_THRESHOLD_G_PER_HOUR = 80

# Source: Styrkr review — 10g is the upper bound per increase week (every 2-3 weeks)
MAX_WEEKLY_INCREASE_ABSOLUTE_G = 10

# Source: Jeukendrup 2011 — 2:1 glucose:fructose
RATIO_PHASE_2_GLUCOSE_PCT = 67

# Source: Rowlands et al. 2015 — 1:0.8 glucose:fructose
RATIO_PHASE_3_GLUCOSE_PCT = 56

# Source: Stellingwerff 2012 case study
OPTIMAL_PROTOCOL_WEEKS = 16

# Source: Styrkr review — 8-12 weeks minimum
MIN_PROTOCOL_WEEKS = 8

# ── Placeholder constants — validate with sports nutritionist ─────────────────

# Insert a hold (consolidation) week every N weeks so adaptation can solidify
CONSOLIDATION_INTERVAL_WEEKS = 3

# Reduce starting carbs when the athlete has a GI distress history
GI_HISTORY_NONE_MULTIPLIER = 1.0
GI_HISTORY_OCCASIONAL_MULTIPLIER = 0.85
GI_HISTORY_FREQUENT_MULTIPLIER = 0.70

# Phase thresholds (week numbers, inclusive)
RATIO_PHASE_1_UNTIL_WEEK = 4   # Weeks 1–4:  100% glucose
RATIO_PHASE_2_UNTIL_WEEK = 10  # Weeks 5–10: 2:1 ratio

# Reduce load in the final weeks before race
# (current research leans toward maintaining or increasing — revisit with nutritionist)
TAPER_WEEKS = 2
TAPER_LOAD_FRACTION = 0.75

# Weekly progression bounds — actual increase = clamp(fraction * current, min, max)
MAX_WEEKLY_INCREASE_FRACTION = 0.15
MIN_WEEKLY_INCREASE_ABSOLUTE_G = 5

# Refuse plan generation if fewer than this many weeks remain to race
ABSOLUTE_MINIMUM_WEEKS_TO_RACE = 4

# ── Fueling window timing ─────────────────────────────────────────────────────
FUELING_WARMUP_MINUTES = 30    # Wait this long after session start before first gel
FUELING_INTERVAL_MINUTES = 30  # Then one gel intake every N minutes

# ── Gel sizes (fixed product SKUs) ───────────────────────────────────────────
SMALL_GEL_CARBS_G = 25
LARGE_GEL_CARBS_G = 40
