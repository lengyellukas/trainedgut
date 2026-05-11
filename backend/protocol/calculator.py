import math
from datetime import date, timedelta
from typing import Dict

from . import config
from .inputs import CarbToleranceOption, GIHistory, SessionDurationOption, StartPreference


# Maps each tolerance option to grams per hour of carbs the athlete currently handles
CARB_TOLERANCE_G_PER_HOUR: Dict[CarbToleranceOption, int] = {
    CarbToleranceOption.NEVER_USED: 0,
    CarbToleranceOption.OCCASIONAL_ONE_GEL: 20,
    CarbToleranceOption.REGULAR_ONE_TWO: 45,
    CarbToleranceOption.COMFORTABLE_TWO_PLUS: 70,
}

GI_HISTORY_MULTIPLIER: Dict[GIHistory, float] = {
    GIHistory.NONE: config.GI_HISTORY_NONE_MULTIPLIER,
    GIHistory.OCCASIONAL: config.GI_HISTORY_OCCASIONAL_MULTIPLIER,
    GIHistory.FREQUENT: config.GI_HISTORY_FREQUENT_MULTIPLIER,
}

SESSION_FUELING_WINDOWS: Dict[SessionDurationOption, int] = {
    SessionDurationOption.BETWEEN_90MIN_AND_2H: 2,
    SessionDurationOption.BETWEEN_2H_AND_3H: 4,
    SessionDurationOption.BETWEEN_3H_AND_4H: 6,
    SessionDurationOption.BETWEEN_4H_AND_6H: 10,
    SessionDurationOption.OVER_6H: 12,
}


def calculate_starting_carbs(
    carb_tolerance: CarbToleranceOption,
    gi_history: GIHistory,
) -> int:
    """Week-1 carb target, rounded to nearest 5 g/hr."""
    raw = CARB_TOLERANCE_G_PER_HOUR[carb_tolerance]
    adjusted = raw * GI_HISTORY_MULTIPLIER[gi_history]
    # Never start below the research-backed floor, even for very cautious profiles
    floored = max(config.MIN_STARTING_CARBS_G_PER_HOUR, adjusted)
    return round(floored / 5) * 5


def calculate_week_increase(current_carbs_g: int) -> int:
    """How many g/hr to add this week, within research-backed bounds, rounded to 5."""
    fraction_based = current_carbs_g * config.MAX_WEEKLY_INCREASE_FRACTION
    clamped = max(
        config.MIN_WEEKLY_INCREASE_ABSOLUTE_G,
        min(config.MAX_WEEKLY_INCREASE_ABSOLUTE_G, fraction_based),
    )
    return round(clamped / 5) * 5


def calculate_carb_ceiling(peak_reachable_g: int) -> int:
    """Choose between standard (90) and elite (120) ceiling based on projected peak."""
    if peak_reachable_g >= config.ELITE_UNLOCK_THRESHOLD_G_PER_HOUR:
        return config.ELITE_CARB_CEILING_G_PER_HOUR
    return config.STANDARD_CARB_CEILING_G_PER_HOUR


def calculate_start_date(
    start_preference: StartPreference,
    preferred_start_date: date,
    race_date: date,
    today: date,
) -> date:
    if start_preference == StartPreference.IMMEDIATELY:
        return today
    if start_preference == StartPreference.SPECIFIC_DATE:
        return preferred_start_date
    # OPTIMAL: work back from race_date for the ideal protocol length
    return race_date - timedelta(weeks=config.OPTIMAL_PROTOCOL_WEEKS)


def calculate_weeks_to_race(start_date: date, race_date: date) -> int:
    return max(0, (race_date - start_date).days // 7)


def calculate_fueling_window_time(window_number: int) -> int:
    """Minutes from session start for the nth fueling window (1-indexed)."""
    return config.FUELING_WARMUP_MINUTES + (window_number - 1) * config.FUELING_INTERVAL_MINUTES


def calculate_carbs_per_window(carbs_per_hour_g: int) -> int:
    """Grams of carbs the athlete should take in each fueling window."""
    return round(carbs_per_hour_g * config.FUELING_INTERVAL_MINUTES / 60)


def n_fueling_windows(duration_option: SessionDurationOption) -> int:
    return SESSION_FUELING_WINDOWS[duration_option]
