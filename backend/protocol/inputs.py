from enum import Enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class SportType(str, Enum):
    RUNNING = "running"
    TRIATHLON = "triathlon"
    CYCLING = "cycling"

    OBSTACLE_RACE = "obstacle_race"
    DUATHLON = "duathlon"
    SWIMMING = "swimming"


class CarbToleranceOption(str, Enum):
    NEVER_USED = "never_used"                    # ~0 g/hr current tolerance
    OCCASIONAL_ONE_GEL = "occasional_one_gel"    # ~20 g/hr
    REGULAR_ONE_TWO = "regular_one_two"          # ~45 g/hr
    COMFORTABLE_TWO_PLUS = "comfortable_two_plus"  # ~70 g/hr


class SessionDurationOption(str, Enum):
    BETWEEN_90MIN_AND_2H = "90min_to_2h"  # 2 fueling windows
    BETWEEN_2H_AND_3H = "2h_to_3h"        # 4 fueling windows
    BETWEEN_3H_AND_4H = "3h_to_4h"        # 6 fueling windows
    BETWEEN_4H_AND_6H = "4h_to_6h"        # 10 fueling windows
    OVER_6H = "over_6h"                    # 12 fueling windows


class GIHistory(str, Enum):
    NONE = "none"             # No GI issues — start at full tolerance
    OCCASIONAL = "occasional" # Some GI issues — start at 85% of tolerance
    FREQUENT = "frequent"     # Frequent GI issues — start at 70% of tolerance


class StartPreference(str, Enum):
    IMMEDIATELY = "immediately"        # Start today
    SPECIFIC_DATE = "specific_date"    # Use preferred_start_date field
    OPTIMAL = "optimal"                # Work back from race_date


class LongSession(BaseModel):
    duration_option: SessionDurationOption


class AthleteProfile(BaseModel):
    body_weight_kg: float
    sport_type: SportType
    target_race_time_hours: float
    race_date: date
    start_preference: StartPreference
    preferred_start_date: Optional[date] = None
    carb_tolerance_option: CarbToleranceOption
    gi_history: GIHistory
    long_sessions: List[LongSession]
