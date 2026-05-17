from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from protocol.inputs import AthleteProfile
from protocol.models import GeneratePlanResponse, PlanStatus
from protocol.generator import generate_plan
from database import get_db
from persistence import save_plan, save_feedback, save_extra_session, find_or_create_athlete, list_extra_sessions, load_active_plan_response, delete_active_plan, load_gel_options
from auth import get_current_user

app = FastAPI(title="TrainedGut API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trainedgut.store",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


class FeedbackRequest(BaseModel):
    week_number: int
    session_number: int
    status: str = "completed"                # completed / skipped
    consumed_vs_plan: str | None = None      # less / as_planned / more (required when completed)
    consumed_ratio: float | None = None      # required when completed
    gi_scale: int | None = None              # 0=none 1=mild 2=moderate 3=severe (required when completed)


class ExtraSessionRequest(BaseModel):
    week_number: int
    duration_option: str
    n_small_gels_consumed: int = 0
    n_large_gels_consumed: int = 0
    gi_scale: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def get_me(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lazy-create the athlete row on first authenticated request."""
    athlete = find_or_create_athlete(db, email=user["email"], supabase_user_id=user["sub"])
    return {
        "email": athlete.email,
        "supabase_user_id": athlete.supabase_user_id,
        "athlete_id": athlete.id,
        "age": athlete.age,
        "weight_kg": athlete.weight_kg,
        "height_cm": athlete.height_cm,
    }


@app.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan_endpoint(
    request: AthleteProfile,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    available_gels = load_gel_options(db, brand=request.gel_brand.value, market=request.market.value if request.market else None)
    response = generate_plan(request, available_gels=available_gels, today=date.today())

    if response.status != PlanStatus.TOO_SHORT:
        save_plan(db, email=user["email"], supabase_user_id=user["sub"], profile=request, plan=response.plan)

    return response


@app.get("/plan", response_model=GeneratePlanResponse | None)
def get_active_plan_endpoint(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reconstruct and return the user's active plan response from DB tables, or null."""
    return load_active_plan_response(db, supabase_user_id=user["sub"])


@app.delete("/plan", status_code=204)
def delete_active_plan_endpoint(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the user's currently active plan (cascades to weeks/sessions/windows/feedback/extras)."""
    if not delete_active_plan(db, supabase_user_id=user["sub"]):
        raise HTTPException(status_code=404, detail="No active plan to delete")
    return


@app.post("/feedback", status_code=201)
def submit_feedback_endpoint(
    request: FeedbackRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.status not in ("completed", "skipped"):
        raise HTTPException(status_code=400, detail="status must be 'completed' or 'skipped'")
    if request.status == "completed" and (
        request.consumed_vs_plan is None or request.consumed_ratio is None or request.gi_scale is None
    ):
        raise HTTPException(status_code=400, detail="completed feedback requires consumed_vs_plan, consumed_ratio, gi_scale")

    result = save_feedback(
        db,
        supabase_user_id=user["sub"],
        week_number=request.week_number,
        session_number=request.session_number,
        status=request.status,
        consumed_vs_plan=request.consumed_vs_plan,
        consumed_ratio=request.consumed_ratio,
        gi_scale=request.gi_scale,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Session not found for this user and week/session numbers")
    return {"status": "ok"}


@app.post("/extra-session", status_code=201)
def submit_extra_session_endpoint(
    request: ExtraSessionRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = save_extra_session(
        db,
        supabase_user_id=user["sub"],
        week_number=request.week_number,
        duration_option=request.duration_option,
        n_small_gels_consumed=request.n_small_gels_consumed,
        n_large_gels_consumed=request.n_large_gels_consumed,
        gi_scale=request.gi_scale,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Week not found for this user and week number")
    return {"status": "ok"}


@app.get("/extra-sessions")
def list_extra_sessions_endpoint(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all unplanned sessions logged against the user's active plan."""
    return list_extra_sessions(db, supabase_user_id=user["sub"])
