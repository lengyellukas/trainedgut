# TrainedGut — Claude Agent Context

## What this project is

A personalised gut training protocol system for endurance athletes.
The core product is a structured plan (8-20 weeks, typically 16) that
progressively trains an athlete's gut to tolerate high carbohydrate intake
during exercise — paired with a physical package of gels delivered to the athlete.

The product is built by Lukas, a solo founder with an IT background. The guiding
principle is honesty and precision — every number should be grounded in research
or explicitly flagged as a placeholder for the sports nutritionist to validate.

---

## Project structure

```
trained-gut/                         ← root of the entire project
├── CLAUDE.md                       ← you are here
├── frontend/                       ← HTML/CSS landing page
│   └── index.html                  ← main landing page (email signup, research citations)
└── backend/                        ← Python API and protocol logic
    ├── api.py                      ← FastAPI layer, HTTP endpoints
    ├── main.py                     ← local test script, not part of product
    └── protocol/
        ├── __init__.py
        ├── config.py               ← ALL tunable constants live here, nowhere else
        ├── inputs.py               ← athlete profile, enums, input data structures
        ├── models.py               ← output data structures (Plan, Week, Session etc.)
        ├── gels.py                 ← gel catalogue, selection logic, package summary
        ├── calculator.py           ← pure calculation functions, no side effects
        └── generator.py           ← assembles the plan by calling calculator functions
```

---

## How to run locally

### Frontend
Open `frontend/index.html` directly in a browser — no server needed for the
landing page. It is a static HTML file.

### Backend
```bash
# Navigate to backend
cd trained-gut/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Install dependencies
pip install fastapi uvicorn pydantic

# Run test script (prints plans to terminal)
python main.py

# Run API server (hot reload on file save)
uvicorn api:app --reload

# API available at:
# http://localhost:8000
# http://localhost:8000/docs        ← interactive docs, use this for quick testing
```

---

## Key design decisions — do not change without reason

### config.py is the single source of truth for all numbers
No magic numbers anywhere in calculator.py or generator.py. Every constant
that a sports nutritionist might want to adjust lives in config.py with a
comment explaining its source (research-backed or placeholder).

### Hard logic only — no AI in the protocol generator
The plan is deterministic. Same inputs always produce the same output.
This is intentional — the product needs to be auditable and honest.

### Always whole gels — never half gels
The gel selection algorithm in gels.py always recommends whole gels only.
If the target cannot be hit exactly, it overshoots slightly and notes the
difference. Do not change this behaviour.

### Three gel sizes, two carb sizes, three ratio phases = six SKUs
- Small gel: 25g carbs
- Large gel: 40g carbs
- Phase 1: 100% glucose (weeks 1-4)
- Phase 2: 67% glucose / 33% fructose — 2:1 ratio (weeks 5-10)
- Phase 3: 56% glucose / 44% fructose — 1:0.8 ratio (weeks 11+)

Phase thresholds are in config.py as RATIO_PHASE_1_UNTIL_WEEK and
RATIO_PHASE_2_UNTIL_WEEK.

### Plan status is always returned — never a raw error
Even a refused plan (TOO_SHORT) returns a structured GeneratePlanResponse
with status and status_message. The frontend always gets something it can
display. Do not raise HTTP exceptions for business logic failures — only
for malformed requests.

### Fueling windows start after warmup and repeat on interval
Defined in config.py as FUELING_WARMUP_MINUTES and FUELING_INTERVAL_MINUTES.
Currently 30 min warmup, then every 30 min. May change to every 20 min at
high carb loads after nutritionist consultation.

---

## Enums reference

### SportType (inputs.py)
```
MARATHON, ULTRA_TRAIL, TRAIL_RUNNING
IRONMAN, HALF_IRONMAN, TRIATHLON_SPRINT_OLYMPIC
GRAN_FONDO, CYCLING_ENDURANCE
HYROX, SPARTAN, OCR
DUATHLON, SWIMRUN
```

### CarbToleranceOption (inputs.py)
```
NEVER_USED           → 0 g/hr
OCCASIONAL_ONE_GEL   → 20 g/hr
REGULAR_ONE_TWO      → 45 g/hr
COMFORTABLE_TWO_PLUS → 70 g/hr
```

### SessionDurationOption (inputs.py)
```
BETWEEN_90MIN_AND_2H → 2 fueling windows
BETWEEN_2H_AND_3H    → 4 fueling windows
BETWEEN_3H_AND_4H    → 6 fueling windows
OVER_4H              → 8 fueling windows
```

### GIHistory (inputs.py)
```
NONE       → start at full current tolerance
OCCASIONAL → start at 85% of current tolerance
FREQUENT   → start at 70% of current tolerance
```

### StartPreference (inputs.py)
```
IMMEDIATELY   → start today
SPECIFIC_DATE → use preferred_start_date field (required)
OPTIMAL       → work backwards from race_date
```

### PlanStatus (models.py)
```
VALID       → plan generated normally
TOO_SHORT   → not enough time, no plan generated, weeks list is empty
STARTS_LATE → plan generated but starts in the future
```

---

## API endpoints

### GET /health
Returns `{"status": "ok"}`. Use to confirm server is running.

### POST /generate-plan
Accepts a JSON body matching GeneratePlanRequest. Returns GeneratePlanResponse.

Example request body:
```json
{
  "body_weight_kg": 75,
  "sport_type": "ironman",
  "target_race_time_hours": 12.0,
  "race_date": "2026-09-20",
  "start_preference": "immediately",
  "preferred_start_date": null,
  "carb_tolerance_option": "never_used",
  "gi_history": "occasional",
  "long_sessions": [
    {"duration_option": "2h_to_3h"},
    {"duration_option": "over_4h"}
  ]
}
```

---

## Constants that are research-backed (do not change without a source)

| Constant | Value | Source |
|---|---|---|
| MIN_STARTING_CARBS_G_PER_HOUR | 30 | Styrkr gut training review |
| STANDARD_CARB_CEILING_G_PER_HOUR | 90 | Jeukendrup 2008 |
| ELITE_CARB_CEILING_G_PER_HOUR | 120 | ScienceDirect 2026 review |
| ELITE_UNLOCK_THRESHOLD_G_PER_HOUR | 80 | Product logic — validate with nutritionist |
| MAX_WEEKLY_INCREASE_ABSOLUTE_G | 10 | Styrkr review: 10g per 2-3 weeks |
| RATIO_PHASE_2_GLUCOSE_PCT | 67 | Jeukendrup 2011 (2:1 ratio) |
| RATIO_PHASE_3_GLUCOSE_PCT | 56 | Rowlands et al. 2015 (1:0.8 ratio) |
| OPTIMAL_PROTOCOL_WEEKS | 16 | Stellingwerff 2012 case study |
| MIN_PROTOCOL_WEEKS | 8 | Styrkr review: 8-12 weeks minimum |

## Constants that are placeholders (validate with sports nutritionist)

- CONSOLIDATION_INTERVAL_WEEKS
- GI_HISTORY_START_MULTIPLIER values
- GI_STRESS_START_MULTIPLIER values
- RATIO_PHASE_1_UNTIL_WEEK and RATIO_PHASE_2_UNTIL_WEEK
- TAPER_WEEKS and TAPER_LOAD_FRACTION (research suggests increasing, not tapering)
- MAX_WEEKLY_INCREASE_FRACTION
- MIN_WEEKLY_INCREASE_ABSOLUTE_G
- ABSOLUTE_MINIMUM_WEEKS_TO_RACE

---

## What is not built yet (next steps)

- [ ] Database layer — currently stateless, no plans are persisted
- [ ] User authentication — no login system yet
- [ ] Payment integration — Stripe, gated access to /generate-plan
- [ ] Frontend form — HTML form that POSTs to backend /generate-plan
- [ ] PDF plan output — generate a downloadable plan document
- [ ] Email delivery — send plan to athlete after purchase
- [ ] Admin view — see generated plans, manage orders
- [ ] Deployment — VPS setup, domain trainedgut.store pointing to server

---

## Code style conventions

- Functions are short — one function does one thing
- Every non-obvious line has a comment explaining why, not just what
- Private functions in generator.py are prefixed with underscore _
- All constants are UPPER_SNAKE_CASE and live in config.py
- Enums are used for all fixed option sets — no raw strings in logic
- Pydantic models in api.py are suffixed with Request or Response
- No print statements in protocol/ files — only in main.py

---

## Domain and hosting

- Domain: trainedgut.store (registered via WebSupport.sk)
- Planned hosting: Hetzner or DigitalOcean VPS, or Railway/Render free tier
- Stack: Python + FastAPI + uvicorn, no framework beyond that for now

---

## Important business context

- This is a validation-first startup — landing page email signups before full launch
- The nutritionist session will refine placeholder constants in config.py
- Whole foods are mentioned in coaching notes only — not part of protocol logic
- The plan and the gel package are inseparable — the product is both together
- Honest, precise language throughout — no inflated claims, real citations only
