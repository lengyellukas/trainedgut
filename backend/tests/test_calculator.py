from datetime import date, timedelta

import pytest

from protocol import config
from protocol.calculator import (
    calculate_carb_ceiling,
    calculate_carbs_per_window,
    calculate_fueling_window_time,
    calculate_start_date,
    calculate_starting_carbs,
    calculate_week_increase,
    calculate_weeks_to_race,
    n_fueling_windows,
)
from protocol.inputs import (
    CarbToleranceOption, GIHistory, SessionDurationOption, StartPreference,
)


class TestStartingCarbs:
    def test_never_used_no_gi_history_floors_at_minimum(self):
        # 0 g/hr tolerance × 1.0 multiplier → floor to 30
        result = calculate_starting_carbs(
            CarbToleranceOption.NEVER_USED, GIHistory.NONE
        )
        assert result == config.MIN_STARTING_CARBS_G_PER_HOUR

    def test_never_used_frequent_gi_still_floors_at_minimum(self):
        # 0 × 0.70 = 0 → floor to 30
        result = calculate_starting_carbs(
            CarbToleranceOption.NEVER_USED, GIHistory.FREQUENT
        )
        assert result == config.MIN_STARTING_CARBS_G_PER_HOUR

    def test_occasional_gel_no_gi_history(self):
        # 20 × 1.0 = 20 → floor to 30
        result = calculate_starting_carbs(
            CarbToleranceOption.OCCASIONAL_ONE_GEL, GIHistory.NONE
        )
        assert result == 30

    def test_regular_one_two_occasional_gi(self):
        # 45 × 0.85 = 38.25 → round to nearest 5 = 40
        result = calculate_starting_carbs(
            CarbToleranceOption.REGULAR_ONE_TWO, GIHistory.OCCASIONAL
        )
        assert result == 40

    def test_comfortable_no_gi_history(self):
        # 70 × 1.0 = 70 → round to 70
        result = calculate_starting_carbs(
            CarbToleranceOption.COMFORTABLE_TWO_PLUS, GIHistory.NONE
        )
        assert result == 70

    def test_comfortable_frequent_gi(self):
        # 70 × 0.70 = 49 → round to nearest 5 = 50
        result = calculate_starting_carbs(
            CarbToleranceOption.COMFORTABLE_TWO_PLUS, GIHistory.FREQUENT
        )
        assert result == 50

    def test_result_is_multiple_of_5(self):
        for tolerance in CarbToleranceOption:
            for gi in GIHistory:
                result = calculate_starting_carbs(tolerance, gi)
                assert result % 5 == 0, f"{tolerance},{gi} → {result} not multiple of 5"

    def test_result_never_below_minimum(self):
        for tolerance in CarbToleranceOption:
            for gi in GIHistory:
                result = calculate_starting_carbs(tolerance, gi)
                assert result >= config.MIN_STARTING_CARBS_G_PER_HOUR


class TestWeekIncrease:
    def test_low_carbs_floored_to_minimum(self):
        # 30 × 0.15 = 4.5 → clamped to 5 → rounds to 5
        assert calculate_week_increase(30) == 5

    def test_mid_carbs(self):
        # 60 × 0.15 = 9 → clamped to 9 → rounds to 10
        assert calculate_week_increase(60) == 10

    def test_high_carbs_capped_at_maximum(self):
        # 90 × 0.15 = 13.5 → clamped to 10 → rounds to 10
        assert calculate_week_increase(90) == 10

    def test_result_never_below_minimum(self):
        for carbs in range(30, 120, 5):
            assert calculate_week_increase(carbs) >= config.MIN_WEEKLY_INCREASE_ABSOLUTE_G

    def test_result_never_above_maximum(self):
        for carbs in range(30, 120, 5):
            assert calculate_week_increase(carbs) <= config.MAX_WEEKLY_INCREASE_ABSOLUTE_G

    def test_result_is_multiple_of_5(self):
        for carbs in range(30, 120, 5):
            assert calculate_week_increase(carbs) % 5 == 0


class TestCarbCeiling:
    def test_below_threshold_uses_standard_ceiling(self):
        assert calculate_carb_ceiling(70) == config.STANDARD_CARB_CEILING_G_PER_HOUR

    def test_at_threshold_uses_elite_ceiling(self):
        assert calculate_carb_ceiling(config.ELITE_UNLOCK_THRESHOLD_G_PER_HOUR) == config.ELITE_CARB_CEILING_G_PER_HOUR

    def test_above_threshold_uses_elite_ceiling(self):
        assert calculate_carb_ceiling(100) == config.ELITE_CARB_CEILING_G_PER_HOUR


class TestStartDate:
    TODAY = date(2026, 5, 5)
    RACE = date(2026, 9, 20)

    def test_immediately_returns_today(self):
        result = calculate_start_date(
            StartPreference.IMMEDIATELY, None, self.RACE, self.TODAY
        )
        assert result == self.TODAY

    def test_specific_date_returns_that_date(self):
        specific = date(2026, 6, 1)
        result = calculate_start_date(
            StartPreference.SPECIFIC_DATE, specific, self.RACE, self.TODAY
        )
        assert result == specific

    def test_optimal_works_back_from_race(self):
        result = calculate_start_date(
            StartPreference.OPTIMAL, None, self.RACE, self.TODAY
        )
        expected = self.RACE - timedelta(weeks=config.OPTIMAL_PROTOCOL_WEEKS)
        assert result == expected


class TestWeeksToRace:
    def test_exact_weeks(self):
        start = date(2026, 5, 5)
        race = date(2026, 9, 1)  # 119 days = 17 weeks exactly
        assert calculate_weeks_to_race(start, race) == 17

    def test_partial_week_truncated(self):
        start = date(2026, 5, 5)
        race = start + timedelta(days=20)  # 2 weeks + 6 days → 2
        assert calculate_weeks_to_race(start, race) == 2

    def test_same_day_is_zero(self):
        d = date(2026, 5, 5)
        assert calculate_weeks_to_race(d, d) == 0

    def test_race_in_past_is_zero(self):
        start = date(2026, 5, 5)
        race = date(2026, 4, 1)
        assert calculate_weeks_to_race(start, race) == 0


class TestFuelingWindowTime:
    def test_first_window(self):
        assert calculate_fueling_window_time(1) == config.FUELING_WARMUP_MINUTES

    def test_second_window(self):
        expected = config.FUELING_WARMUP_MINUTES + config.FUELING_INTERVAL_MINUTES
        assert calculate_fueling_window_time(2) == expected

    def test_third_window(self):
        expected = config.FUELING_WARMUP_MINUTES + 2 * config.FUELING_INTERVAL_MINUTES
        assert calculate_fueling_window_time(3) == expected


class TestCarbsPerWindow:
    def test_30g_per_hour_at_30min_interval(self):
        # 30 × (30/60) = 15
        assert calculate_carbs_per_window(30) == 15

    def test_60g_per_hour_at_30min_interval(self):
        assert calculate_carbs_per_window(60) == 30

    def test_90g_per_hour_at_30min_interval(self):
        assert calculate_carbs_per_window(90) == 45

    def test_120g_per_hour_at_30min_interval(self):
        assert calculate_carbs_per_window(120) == 60


class TestFuelingWindows:
    def test_90min_to_2h_has_2_windows(self):
        assert n_fueling_windows(SessionDurationOption.BETWEEN_90MIN_AND_2H) == 2

    def test_2h_to_3h_has_4_windows(self):
        assert n_fueling_windows(SessionDurationOption.BETWEEN_2H_AND_3H) == 4

    def test_3h_to_4h_has_6_windows(self):
        assert n_fueling_windows(SessionDurationOption.BETWEEN_3H_AND_4H) == 6

    def test_4h_to_6h_has_10_windows(self):
        assert n_fueling_windows(SessionDurationOption.BETWEEN_4H_AND_6H) == 10

    def test_over_6h_has_12_windows(self):
        assert n_fueling_windows(SessionDurationOption.OVER_6H) == 12
