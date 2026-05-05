from enum import Enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class PlanStatus(str, Enum):
    VALID = "valid"
    TOO_SHORT = "too_short"
    STARTS_LATE = "starts_late"


class GelRatio(str, Enum):
    GLUCOSE_100 = "100% glucose"
    RATIO_2_1 = "67% glucose / 33% fructose (2:1)"
    RATIO_1_08 = "56% glucose / 44% fructose (1:0.8)"


class FuelingWindow(BaseModel):
    window_number: int
    time_from_start_minutes: int
    target_carbs_g: int
    actual_carbs_g: int       # may exceed target — whole gels only, never half
    gel_count: int
    n_large_gels: int         # 40g gels
    n_small_gels: int         # 25g gels
    gel_ratio: GelRatio


class Session(BaseModel):
    session_number: int
    duration_option: str
    n_fueling_windows: int
    carbs_per_hour_g: int
    total_target_carbs_g: int
    total_actual_carbs_g: int
    fueling_windows: List[FuelingWindow]


class Week(BaseModel):
    week_number: int
    start_date: date
    end_date: date
    target_carbs_per_hour_g: int
    gel_ratio: GelRatio
    is_consolidation: bool     # hold week — no carb increase from previous week
    sessions: List[Session]


class GelPackageSummary(BaseModel):
    # Six SKUs: three phases × two sizes
    small_phase1_count: int    # 25g, 100% glucose
    large_phase1_count: int    # 40g, 100% glucose
    small_phase2_count: int    # 25g, 2:1 ratio
    large_phase2_count: int    # 40g, 2:1 ratio
    small_phase3_count: int    # 25g, 1:0.8 ratio
    large_phase3_count: int    # 40g, 1:0.8 ratio
    total_gels: int


class Plan(BaseModel):
    athlete_body_weight_kg: float
    sport_type: str
    race_date: date
    starting_carbs_per_hour_g: int
    race_target_carbs_per_hour_g: int   # peak carbs reached in the plan
    total_weeks: int
    weeks: List[Week]
    gel_package: GelPackageSummary


class GeneratePlanResponse(BaseModel):
    status: PlanStatus
    status_message: str
    plan: Optional[Plan] = None
