from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from protocol.inputs import AthleteProfile
from protocol.models import GeneratePlanResponse, PlanStatus
from protocol.generator import generate_plan
from database import get_db
from persistence import save_plan, save_feedback, save_extra_session

app = FastAPI(title="TrainedGut API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trainedgut.store",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class GeneratePlanRequest(AthleteProfile):
    email: EmailStr


class FeedbackRequest(BaseModel):
    email: EmailStr
    week_number: int
    session_number: int
    status: str = "completed"                # completed / skipped
    consumed_vs_plan: str | None = None      # less / as_planned / more (required when completed)
    consumed_ratio: float | None = None      # required when completed
    gi_scale: int | None = None              # 0=none 1=mild 2=moderate 3=severe (required when completed)


class ExtraSessionRequest(BaseModel):
    email: EmailStr
    week_number: int
    duration_option: str
    n_small_gels_consumed: int = 0
    n_large_gels_consumed: int = 0
    gi_scale: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan_endpoint(request: GeneratePlanRequest, db: Session = Depends(get_db)):
    response = generate_plan(request, today=date.today())

    if response.status != PlanStatus.TOO_SHORT:
        save_plan(db, request.email, request, response.plan)

    return response


@app.post("/feedback", status_code=201)
def submit_feedback_endpoint(request: FeedbackRequest, db: Session = Depends(get_db)):
    if request.status not in ("completed", "skipped"):
        raise HTTPException(status_code=400, detail="status must be 'completed' or 'skipped'")
    if request.status == "completed" and (
        request.consumed_vs_plan is None or request.consumed_ratio is None or request.gi_scale is None
    ):
        raise HTTPException(status_code=400, detail="completed feedback requires consumed_vs_plan, consumed_ratio, gi_scale")

    result = save_feedback(
        db,
        email=request.email,
        week_number=request.week_number,
        session_number=request.session_number,
        status=request.status,
        consumed_vs_plan=request.consumed_vs_plan,
        consumed_ratio=request.consumed_ratio,
        gi_scale=request.gi_scale,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Session not found for this email and week/session numbers")
    return {"status": "ok"}


@app.post("/extra-session", status_code=201)
def submit_extra_session_endpoint(request: ExtraSessionRequest, db: Session = Depends(get_db)):
    result = save_extra_session(
        db,
        email=request.email,
        week_number=request.week_number,
        duration_option=request.duration_option,
        n_small_gels_consumed=request.n_small_gels_consumed,
        n_large_gels_consumed=request.n_large_gels_consumed,
        gi_scale=request.gi_scale,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Week not found for this email and week number")
    return {"status": "ok"}
