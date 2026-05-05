"""Local test script — not part of the product. Run from the backend/ directory."""
from datetime import date

from protocol.inputs import (
    AthleteProfile, CarbToleranceOption, GIHistory, LongSession,
    SessionDurationOption, SportType, StartPreference,
)
from protocol.generator import generate_plan


def main():
    profile = AthleteProfile(
        body_weight_kg=75,
        sport_type=SportType.IRONMAN,
        target_race_time_hours=12.0,
        race_date=date(2026, 9, 20),
        start_preference=StartPreference.IMMEDIATELY,
        preferred_start_date=None,
        carb_tolerance_option=CarbToleranceOption.NEVER_USED,
        gi_history=GIHistory.OCCASIONAL,
        long_sessions=[
            LongSession(duration_option=SessionDurationOption.BETWEEN_2H_AND_3H),
            LongSession(duration_option=SessionDurationOption.OVER_4H),
        ],
    )

    response = generate_plan(profile, today=date.today())

    print(f"Status:  {response.status.value}")
    print(f"Message: {response.status_message}")

    if not response.plan:
        return

    plan = response.plan
    print(f"\nAthletes: {plan.athlete_body_weight_kg} kg | {plan.sport_type}")
    print(f"Race: {plan.race_date} | {plan.total_weeks} weeks")
    print(f"Starting: {plan.starting_carbs_per_hour_g} g/hr → Peak: {plan.race_target_carbs_per_hour_g} g/hr")

    print("\nWeek  Start       Carbs    Ratio              Flags")
    print("─" * 65)
    for week in plan.weeks:
        flags = []
        if week.is_consolidation:
            flags.append("HOLD")
        if week.week_number > plan.total_weeks - 2:
            flags.append("TAPER")
        flag_str = " ".join(flags)
        print(
            f"  {week.week_number:2d}  {week.start_date}  "
            f"{week.target_carbs_per_hour_g:3d} g/hr  "
            f"{week.gel_ratio.value:<33}  {flag_str}"
        )

    pkg = plan.gel_package
    print("\nGel Package Summary")
    print("─" * 40)
    print(f"  Phase 1 (100% glucose):      {pkg.small_phase1_count:3d} small  {pkg.large_phase1_count:3d} large")
    print(f"  Phase 2 (2:1 ratio):         {pkg.small_phase2_count:3d} small  {pkg.large_phase2_count:3d} large")
    print(f"  Phase 3 (1:0.8 ratio):       {pkg.small_phase3_count:3d} small  {pkg.large_phase3_count:3d} large")
    print(f"  Total: {pkg.total_gels} gels")

    # Show first week's sessions in detail as a sample
    if plan.weeks:
        week1 = plan.weeks[0]
        print(f"\nWeek 1 session detail (sample):")
        for session in week1.sessions:
            print(f"\n  Session {session.session_number}: {session.duration_option} | "
                  f"{session.n_fueling_windows} windows | "
                  f"{session.total_actual_carbs_g}g total")
            for w in session.fueling_windows:
                print(f"    T+{w.time_from_start_minutes:3d}min: "
                      f"{w.n_large_gels}× large + {w.n_small_gels}× small "
                      f"= {w.actual_carbs_g}g (target {w.target_carbs_g}g)")


if __name__ == "__main__":
    main()
