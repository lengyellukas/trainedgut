from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from protocol.inputs import AthleteProfile
from protocol.models import GeneratePlanResponse
from protocol.generator import generate_plan

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan_endpoint(profile: AthleteProfile):
    return generate_plan(profile, today=date.today())
