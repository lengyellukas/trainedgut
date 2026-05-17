from datetime import date, timedelta
from typing import List

from . import config
from .inputs import AthleteProfile, LongSession
from .models import (
    FuelingWindow, GelOption, GelRatio, GeneratePlanResponse,
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


def _ratio_to_phase(ratio: GelRatio) -> int:
    if ratio == GelRatio.GLUCOSE_100:
        return 1
    if ratio == GelRatio.RATIO_2_1:
        return 2
    return 3


def _build_fueling_window(
    window_number: int,
    target_carbs_g: int,
    gel_ratio: GelRatio,
    available_gels: List[GelOption],
) -> FuelingWindow:
    phase = _ratio_to_phase(gel_ratio)
    options = [g for g in available_gels if g.ratio_phase == phase]
    gels = select_gels(target_carbs_g, options)
    actual = sum(g.carbs_g * g.quantity for g in gels)
    gel_count = sum(g.quantity for g in gels)
    return FuelingWindow(
        window_number=window_number,
        time_from_start_minutes=calculate_fueling_window_time(window_number),
        target_carbs_g=target_carbs_g,
        actual_carbs_g=actual,
        overshoot_g=actual - target_carbs_g,
        gel_count=gel_count,
        gels=gels,
        gel_ratio=gel_ratio,
    )


def _build_session(
    session_number: int,
    long_session: LongSession,
    target_carbs_per_hour_g: int,
    gel_ratio: GelRatio,
    available_gels: List[GelOption],
) -> Session:
    n_windows = n_fueling_windows(long_session.duration_option)
    carbs_per_window = calculate_carbs_per_window(target_carbs_per_hour_g)

    windows = [
        _build_fueling_window(i + 1, carbs_per_window, gel_ratio, available_gels)
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
    end_date: date,
    target_carbs_per_hour_g: int,
    is_consolidation: bool,
    long_sessions: List[LongSession],
    available_gels: List[GelOption],
) -> Week:
    gel_ratio = _gel_ratio_for_week(week_number)
    sessions = [
        _build_session(i + 1, ls, target_carbs_per_hour_g, gel_ratio, available_gels)
        for i, ls in enumerate(long_sessions)
    ]
    return Week(
        week_number=week_number,
        start_date=start_date,
        end_date=end_date,
        target_carbs_per_hour_g=target_carbs_per_hour_g,
        gel_ratio=gel_ratio,
        is_consolidation=is_consolidation,
        sessions=sessions,
    )


def _calendar_week_boundaries(plan_start: date, total_weeks: int) -> List[tuple[date, date]]:
    """Return (start, end) date pairs aligned to Monday–Sunday calendar weeks.

    Week 1 runs from `plan_start` to the next Sunday (1–7 days, depending on weekday).
    Subsequent weeks always run Monday → Sunday.
    """
    # Python: Monday=0 ... Sunday=6. Days until the upcoming Sunday inclusive.
    days_until_sunday = 6 - plan_start.weekday()
    boundaries = [(plan_start, plan_start + timedelta(days=days_until_sunday))]

    cursor = boundaries[0][1] + timedelta(days=1)  # Monday after the first partial week
    for _ in range(total_weeks - 1):
        end = cursor + timedelta(days=6)
        boundaries.append((cursor, end))
        cursor = end + timedelta(days=1)

    return boundaries


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


def generate_plan(
    profile: AthleteProfile,
    available_gels: List[GelOption],
    today: date = None,
) -> GeneratePlanResponse:
    if today is None:
        today = date.today()

    if not available_gels:
        return GeneratePlanResponse(
            status=PlanStatus.TOO_SHORT,
            status_message=(
                f"No gels available for brand '{profile.gel_brand.value}'"
                + (f" in market '{profile.market.value}'." if profile.market else ".")
                + " Pick a different brand or market."
            ),
        )

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

    # Check the chosen brand has gels for every phase the plan will actually use.
    needed_phases = {1}
    if total_weeks > config.RATIO_PHASE_1_UNTIL_WEEK:
        needed_phases.add(2)
    if total_weeks > config.RATIO_PHASE_2_UNTIL_WEEK:
        needed_phases.add(3)
    available_phases = {g.ratio_phase for g in available_gels}
    missing = sorted(needed_phases - available_phases)
    if missing:
        return GeneratePlanResponse(
            status=PlanStatus.TOO_SHORT,
            status_message=(
                f"Brand '{profile.gel_brand.value}' has no gels for ratio phase(s) "
                f"{', '.join(map(str, missing))} which this {total_weeks}-week plan needs. "
                "Pick a different brand or shorten the plan."
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

    boundaries = _calendar_week_boundaries(start_date, total_weeks)

    weeks: List[Week] = []
    for i, (target_carbs, (week_start, week_end)) in enumerate(zip(carb_progression, boundaries)):
        week_number = i + 1
        is_taper = week_number > total_weeks - taper_weeks
        # Consolidation weeks only apply outside the taper
        is_consolidation = (
            not is_taper
            and week_number % config.CONSOLIDATION_INTERVAL_WEEKS == 0
        )
        week = _build_week(
            week_number=week_number,
            start_date=week_start,
            end_date=week_end,
            target_carbs_per_hour_g=target_carbs,
            is_consolidation=is_consolidation,
            long_sessions=profile.long_sessions,
            available_gels=available_gels,
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
