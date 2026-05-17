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


class GelOption(BaseModel):
    """A single available gel product (a row from the gels catalogue)."""
    id: str               # opaque identifier (Gel.id when sourced from DB)
    brand: str
    carbs_g: int
    size_label: str       # 'small' / 'large' / etc — descriptive only
    ratio_phase: int      # 1, 2, or 3


class GelEntry(BaseModel):
    """One product + how many to consume in a window or across the plan."""
    gel_id: str
    brand: str
    carbs_g: int
    size_label: str
    quantity: int


class FuelingWindow(BaseModel):
    window_number: int
    time_from_start_minutes: int
    target_carbs_g: int       # what the protocol asks for
    actual_carbs_g: int       # what the chosen gels actually deliver (>= target)
    overshoot_g: int          # actual - target
    gel_count: int            # total gels consumed in this window
    gels: List[GelEntry]      # which specific gels and how many
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


class GelPackageItem(BaseModel):
    """One line in the package summary: how many of one specific product to order."""
    gel_id: str
    brand: str
    size_label: str
    carbs_g: int
    ratio_phase: int
    quantity: int


class GelPackageSummary(BaseModel):
    items: List[GelPackageItem]   # one entry per distinct product used in the plan
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
