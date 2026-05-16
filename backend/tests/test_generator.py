from datetime import date

import pytest

from protocol import config
from protocol.generator import generate_plan
from protocol.inputs import (
    AthleteProfile, CarbToleranceOption, GIHistory, LongSession,
    SessionDurationOption, SportType, StartPreference,
)
from protocol.models import GelRatio, PlanStatus


def _make_profile(**overrides) -> AthleteProfile:
    defaults = dict(
        body_weight_kg=70,
        sport_type=SportType.TRIATHLON,
        target_race_time_hours=11.0,
        race_date=date(2026, 9, 20),
        start_preference=StartPreference.IMMEDIATELY,
        preferred_start_date=None,
        carb_tolerance_option=CarbToleranceOption.NEVER_USED,
        gi_history=GIHistory.NONE,
        long_sessions=[
            LongSession(duration_option=SessionDurationOption.BETWEEN_2H_AND_3H),
        ],
    )
    defaults.update(overrides)
    return AthleteProfile(**defaults)


TODAY = date(2026, 5, 5)


class TestPlanStatus:
    def test_valid_plan_with_enough_time(self):
        response = generate_plan(_make_profile(), today=TODAY)
        assert response.status == PlanStatus.VALID
        assert response.plan is not None

    def test_too_short_returns_no_plan(self):
        # Race in 2 weeks — below ABSOLUTE_MINIMUM_WEEKS_TO_RACE (4)
        close_race = TODAY + __import__("datetime").timedelta(weeks=2)
        response = generate_plan(_make_profile(race_date=close_race), today=TODAY)
        assert response.status == PlanStatus.TOO_SHORT
        assert response.plan is None
        assert "2 week" in response.status_message

    def test_starts_late_when_optimal_start_is_in_future(self):
        # OPTIMAL start = race_date - 16 weeks = 2026-06-14, which is after today
        response = generate_plan(
            _make_profile(start_preference=StartPreference.OPTIMAL),
            today=TODAY,
        )
        assert response.status == PlanStatus.STARTS_LATE
        assert response.plan is not None

    def test_immediately_is_always_valid_with_enough_time(self):
        response = generate_plan(
            _make_profile(start_preference=StartPreference.IMMEDIATELY),
            today=TODAY,
        )
        assert response.status == PlanStatus.VALID

    def test_specific_future_date_is_starts_late(self):
        future = date(2026, 7, 1)
        response = generate_plan(
            _make_profile(
                start_preference=StartPreference.SPECIFIC_DATE,
                preferred_start_date=future,
            ),
            today=TODAY,
        )
        assert response.status == PlanStatus.STARTS_LATE


class TestPlanLength:
    def test_total_weeks_matches_weeks_list(self):
        response = generate_plan(_make_profile(), today=TODAY)
        plan = response.plan
        assert plan.total_weeks == len(plan.weeks)

    def test_week_numbers_are_sequential(self):
        response = generate_plan(_make_profile(), today=TODAY)
        numbers = [w.week_number for w in response.plan.weeks]
        assert numbers == list(range(1, len(numbers) + 1))

    def test_each_week_starts_day_after_previous_ends(self):
        """With calendar-aligned weeks, week N+1 starts the day after week N ends."""
        from datetime import timedelta
        response = generate_plan(_make_profile(), today=TODAY)
        weeks = response.plan.weeks
        for i in range(1, len(weeks)):
            assert weeks[i].start_date == weeks[i - 1].end_date + timedelta(days=1)

    def test_weeks_after_first_are_full_monday_to_sunday(self):
        """Calendar-aligned: weeks 2+ always run Mon-Sun (7 days, start=Mon, end=Sun)."""
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks[1:]:
            assert (week.end_date - week.start_date).days == 6
            assert week.start_date.weekday() == 0  # Monday
            assert week.end_date.weekday() == 6    # Sunday

    def test_first_week_ends_on_sunday(self):
        """Calendar-aligned: first week always ends on a Sunday (length 1-7 days)."""
        response = generate_plan(_make_profile(), today=TODAY)
        first = response.plan.weeks[0]
        assert first.end_date.weekday() == 6  # Sunday
        assert 0 <= (first.end_date - first.start_date).days <= 6


class TestCarbProgression:
    def test_starts_at_calculated_starting_carbs(self):
        response = generate_plan(_make_profile(), today=TODAY)
        plan = response.plan
        assert plan.weeks[0].target_carbs_per_hour_g == plan.starting_carbs_per_hour_g

    def test_non_consolidation_weeks_never_decrease(self):
        response = generate_plan(_make_profile(), today=TODAY)
        weeks = response.plan.weeks
        taper_start = len(weeks) - config.TAPER_WEEKS
        for i in range(1, taper_start):
            if not weeks[i].is_consolidation:
                assert weeks[i].target_carbs_per_hour_g >= weeks[i - 1].target_carbs_per_hour_g

    def test_consolidation_weeks_cause_no_increase_the_following_week(self):
        # Consolidation week shows the value the previous week increased TO.
        # The hold means: no further increase is scheduled, so the week after
        # consolidation stays at the same level as the consolidation week itself.
        response = generate_plan(_make_profile(), today=TODAY)
        weeks = response.plan.weeks
        taper_start = len(weeks) - config.TAPER_WEEKS
        for i, week in enumerate(weeks[:-1]):
            if week.is_consolidation and i + 1 < taper_start:
                assert weeks[i + 1].target_carbs_per_hour_g == week.target_carbs_per_hour_g

    def test_taper_weeks_are_below_peak(self):
        response = generate_plan(_make_profile(), today=TODAY)
        weeks = response.plan.weeks
        taper_weeks = weeks[-config.TAPER_WEEKS:]
        peak = response.plan.race_target_carbs_per_hour_g
        for week in taper_weeks:
            assert week.target_carbs_per_hour_g < peak

    def test_peak_matches_race_target_field(self):
        response = generate_plan(_make_profile(), today=TODAY)
        plan = response.plan
        actual_peak = max(w.target_carbs_per_hour_g for w in plan.weeks)
        assert plan.race_target_carbs_per_hour_g == actual_peak

    def test_carbs_never_exceed_elite_ceiling(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            assert week.target_carbs_per_hour_g <= config.ELITE_CARB_CEILING_G_PER_HOUR


class TestGelRatioPhases:
    def test_early_weeks_are_glucose_only(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            if week.week_number <= config.RATIO_PHASE_1_UNTIL_WEEK:
                assert week.gel_ratio == GelRatio.GLUCOSE_100

    def test_mid_weeks_are_2_1_ratio(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            if config.RATIO_PHASE_1_UNTIL_WEEK < week.week_number <= config.RATIO_PHASE_2_UNTIL_WEEK:
                assert week.gel_ratio == GelRatio.RATIO_2_1

    def test_late_weeks_are_1_08_ratio(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            if week.week_number > config.RATIO_PHASE_2_UNTIL_WEEK:
                assert week.gel_ratio == GelRatio.RATIO_1_08

    def test_session_windows_inherit_week_ratio(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            for session in week.sessions:
                for window in session.fueling_windows:
                    assert window.gel_ratio == week.gel_ratio


class TestSessions:
    def test_session_count_matches_long_sessions_input(self):
        profile = _make_profile(long_sessions=[
            LongSession(duration_option=SessionDurationOption.BETWEEN_2H_AND_3H),
            LongSession(duration_option=SessionDurationOption.OVER_6H),
        ])
        response = generate_plan(profile, today=TODAY)
        for week in response.plan.weeks:
            assert len(week.sessions) == 2

    def test_short_session_has_2_fueling_windows(self):
        profile = _make_profile(long_sessions=[
            LongSession(duration_option=SessionDurationOption.BETWEEN_90MIN_AND_2H),
        ])
        response = generate_plan(profile, today=TODAY)
        for week in response.plan.weeks:
            assert week.sessions[0].n_fueling_windows == 2

    def test_long_session_has_12_fueling_windows(self):
        profile = _make_profile(long_sessions=[
            LongSession(duration_option=SessionDurationOption.OVER_6H),
        ])
        response = generate_plan(profile, today=TODAY)
        for week in response.plan.weeks:
            assert week.sessions[0].n_fueling_windows == 12

    def test_actual_carbs_never_below_target_carbs_per_window(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            for session in week.sessions:
                for window in session.fueling_windows:
                    assert window.actual_carbs_g >= window.target_carbs_g

    def test_window_times_increase_within_session(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            for session in week.sessions:
                times = [w.time_from_start_minutes for w in session.fueling_windows]
                assert times == sorted(times)
                assert times == list(range(times[0], times[-1] + 1, config.FUELING_INTERVAL_MINUTES))

    def test_first_window_starts_after_warmup(self):
        response = generate_plan(_make_profile(), today=TODAY)
        for week in response.plan.weeks:
            for session in week.sessions:
                assert session.fueling_windows[0].time_from_start_minutes == config.FUELING_WARMUP_MINUTES


class TestGelPackage:
    def test_total_gels_matches_sum_of_all_windows(self):
        profile = _make_profile(long_sessions=[
            LongSession(duration_option=SessionDurationOption.BETWEEN_2H_AND_3H),
            LongSession(duration_option=SessionDurationOption.OVER_6H),
        ])
        response = generate_plan(profile, today=TODAY)
        plan = response.plan

        counted = sum(
            w.gel_count
            for week in plan.weeks
            for session in week.sessions
            for w in session.fueling_windows
        )
        assert plan.gel_package.total_gels == counted

    def test_gel_package_counts_are_non_negative(self):
        response = generate_plan(_make_profile(), today=TODAY)
        pkg = response.plan.gel_package
        for field, value in pkg.model_dump().items():
            assert value >= 0, f"{field} is negative: {value}"
