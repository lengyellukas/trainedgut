from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from protocol.inputs import AthleteProfile
from protocol.models import GeneratePlanResponse, PlanStatus
from protocol.generator import generate_plan
from database import get_db
from persistence import save_plan, save_feedback

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
    consumed_vs_plan: str   # less / as_planned / more
    consumed_ratio: float
    gi_scale: int           # 0=none 1=mild 2=moderate 3=severe


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
    result = save_feedback(
        db,
        email=request.email,
        week_number=request.week_number,
        session_number=request.session_number,
        consumed_vs_plan=request.consumed_vs_plan,
        consumed_ratio=request.consumed_ratio,
        gi_scale=request.gi_scale,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Session not found for this email and week/session numbers")
    return {"status": "ok"}
