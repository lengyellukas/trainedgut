from datetime import date, timedelta
from typing import List

from . import config
from .inputs import AthleteProfile, LongSession
from .models import (
    FuelingWindow, GelRatio, GeneratePlanResponse,
    Plan, PlanStatus, Session, Week,
)
from .calculator import (
    calculate_starting_carbs, calculate_week_increase, calculate_start_date,
    calculate_weeks_to_race, calculate_carb_ceiling,
    calculate_fueling_window_time, calculate_carbs_per_window, n_fueling_windows,
)
from .gels import select_gels, summarise_package


def _gel_ratio_for_week(week_number: int) -> GelRatio:
    if week_number <= config.RATIO_PHASE_1_UNTIL_WEEK:
        return GelRatio.GLUCOSE_100
    if week_number <= config.RATIO_PHASE_2_UNTIL_WEEK:
        return GelRatio.RATIO_2_1
    return GelRatio.RATIO_1_08


def _build_fueling_window(
    window_number: int,
    target_carbs_g: int,
    gel_ratio: GelRatio,
) -> FuelingWindow:
    gel = select_gels(target_carbs_g)
    return FuelingWindow(
        window_number=window_number,
        time_from_start_minutes=calculate_fueling_window_time(window_number),
        target_carbs_g=target_carbs_g,
        actual_carbs_g=gel.actual_carbs_g,
        gel_count=gel.n_large + gel.n_small,
        n_large_gels=gel.n_large,
        n_small_gels=gel.n_small,
        gel_ratio=gel_ratio,
    )


def _build_session(
    session_number: int,
    long_session: LongSession,
    target_carbs_per_hour_g: int,
    gel_ratio: GelRatio,
) -> Session:
    n_windows = n_fueling_windows(long_session.duration_option)
    carbs_per_window = calculate_carbs_per_window(target_carbs_per_hour_g)

    windows = [
        _build_fueling_window(i + 1, carbs_per_window, gel_ratio)
        for i in range(n_windows)
    ]

    return Session(
        session_number=session_number,
        duration_option=long_session.duration_option.value,
        n_fueling_windows=n_windows,
        carbs_per_hour_g=target_carbs_per_hour_g,
        total_target_carbs_g=carbs_per_window * n_windows,
        total_actual_carbs_g=sum(w.actual_carbs_g for w in windows),
        fueling_windows=windows,
    )


def _build_week(
    week_number: int,
    start_date: date,
    target_carbs_per_hour_g: int,
    is_consolidation: bool,
    long_sessions: List[LongSession],
) -> Week:
    gel_ratio = _gel_ratio_for_week(week_number)
    sessions = [
        _build_session(i + 1, ls, target_carbs_per_hour_g, gel_ratio)
        for i, ls in enumerate(long_sessions)
    ]
    return Week(
        week_number=week_number,
        start_date=start_date,
        end_date=start_date + timedelta(days=6),
        target_carbs_per_hour_g=target_carbs_per_hour_g,
        gel_ratio=gel_ratio,
        is_consolidation=is_consolidation,
        sessions=sessions,
    )


def _simulate_carb_progression(
    starting_carbs_g: int,
    total_weeks: int,
    taper_weeks: int,
) -> List[int]:
    """
    Week-by-week carb targets.

    Two-pass approach: first simulate with the standard ceiling to find the
    athlete's reachable peak, then pick the correct ceiling (standard vs elite)
    and re-simulate. This prevents the ceiling choice from depending on itself.
    """
    training_weeks = total_weeks - taper_weeks

    def _run(ceiling: int) -> List[int]:
        carbs: List[int] = [0] * total_weeks
        current = starting_carbs_g
        for i in range(training_weeks):
            week_num = i + 1
            is_hold = week_num % config.CONSOLIDATION_INTERVAL_WEEKS == 0
            carbs[i] = current
            if not is_hold and current < ceiling:
                current = min(current + calculate_week_increase(current), ceiling)
        return carbs

    # Pass 1: find peak with conservative ceiling
    carbs_pass1 = _run(config.STANDARD_CARB_CEILING_G_PER_HOUR)
    peak = max(carbs_pass1[:training_weeks]) if training_weeks > 0 else starting_carbs_g

    # Pass 2: re-run with the correct ceiling
    ceiling = calculate_carb_ceiling(peak)
    carbs = _run(ceiling)

    # Taper weeks hold at a fraction of the peak
    peak = max(carbs[:training_weeks]) if training_weeks > 0 else starting_carbs_g
    taper_load = round(peak * config.TAPER_LOAD_FRACTION / 5) * 5
    for i in range(training_weeks, total_weeks):
        carbs[i] = taper_load

    return carbs


def generate_plan(profile: AthleteProfile, today: date = None) -> GeneratePlanResponse:
    if today is None:
        today = date.today()

    start_date = calculate_start_date(
        profile.start_preference,
        profile.preferred_start_date,
        profile.race_date,
        today,
    )

    total_weeks = calculate_weeks_to_race(start_date, profile.race_date)

    if total_weeks < config.ABSOLUTE_MINIMUM_WEEKS_TO_RACE:
        return GeneratePlanResponse(
            status=PlanStatus.TOO_SHORT,
            status_message=(
                f"Only {total_weeks} week(s) until your race. "
                f"A minimum of {config.ABSOLUTE_MINIMUM_WEEKS_TO_RACE} weeks is needed "
                "to begin gut training."
            ),
        )

    status = PlanStatus.VALID
    status_message = "Plan generated successfully."

    if start_date > today:
        status = PlanStatus.STARTS_LATE
        status_message = (
            f"Your plan starts on {start_date.isoformat()}, which is in the future. "
            "The plan is valid but begins after today."
        )

    starting_carbs = calculate_starting_carbs(
        profile.carb_tolerance_option,
        profile.gi_history,
    )

    # Never taper more than 25% of the plan length
    taper_weeks = min(config.TAPER_WEEKS, total_weeks // 4)
    carb_progression = _simulate_carb_progression(starting_carbs, total_weeks, taper_weeks)

    weeks: List[Week] = []
    for i, target_carbs in enumerate(carb_progression):
        week_number = i + 1
        is_taper = week_number > total_weeks - taper_weeks
        # Consolidation weeks only apply outside the taper
        is_consolidation = (
            not is_taper
            and week_number % config.CONSOLIDATION_INTERVAL_WEEKS == 0
        )
        week = _build_week(
            week_number=week_number,
            start_date=start_date + timedelta(weeks=i),
            target_carbs_per_hour_g=target_carbs,
            is_consolidation=is_consolidation,
            long_sessions=profile.long_sessions,
        )
        weeks.append(week)

    peak_carbs = max(w.target_carbs_per_hour_g for w in weeks)

    return GeneratePlanResponse(
        status=status,
        status_message=status_message,
        plan=Plan(
            athlete_body_weight_kg=profile.body_weight_kg,
            sport_type=profile.sport_type.value,
            race_date=profile.race_date,
            starting_carbs_per_hour_g=starting_carbs,
            race_target_carbs_per_hour_g=peak_carbs,
            total_weeks=total_weeks,
            weeks=weeks,
            gel_package=summarise_package(weeks),
        ),
    )
