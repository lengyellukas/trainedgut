from datetime import date

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from protocol.inputs import AthleteProfile
from protocol.models import GeneratePlanResponse, PlanStatus
from protocol.generator import generate_plan
from database import get_db
from persistence import save_plan

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan_endpoint(request: GeneratePlanRequest, db: Session = Depends(get_db)):
    response = generate_plan(request, today=date.today())

    if response.status != PlanStatus.TOO_SHORT:
        save_plan(db, request.email, request, response.plan)

    return response
