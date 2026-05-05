import pytest
from protocol.gels import select_gels, GelSelection


def test_zero_target_returns_no_gels():
    result = select_gels(0)
    assert result.n_large == 0
    assert result.n_small == 0
    assert result.actual_carbs_g == 0


def test_exact_small_gel():
    result = select_gels(25)
    assert result.n_small == 1
    assert result.n_large == 0
    assert result.actual_carbs_g == 25
    assert result.overshoot_g == 0


def test_exact_large_gel():
    result = select_gels(40)
    assert result.n_large == 1
    assert result.n_small == 0
    assert result.actual_carbs_g == 40
    assert result.overshoot_g == 0


def test_prefers_one_large_over_two_small_for_30g():
    # 1 large (40g, overshoot 10) beats 2 small (50g, overshoot 25)
    result = select_gels(30)
    assert result.n_large == 1
    assert result.n_small == 0
    assert result.actual_carbs_g == 40


def test_45g_uses_two_small():
    # 2 small (50g, overshoot 5) beats 1 large+1 small (65g, overshoot 20)
    result = select_gels(45)
    assert result.n_large == 0
    assert result.n_small == 2
    assert result.actual_carbs_g == 50


def test_55g_uses_one_large_one_small():
    result = select_gels(55)
    assert result.n_large == 1
    assert result.n_small == 1
    assert result.actual_carbs_g == 65


def test_60g_uses_one_large_one_small():
    result = select_gels(60)
    assert result.n_large == 1
    assert result.n_small == 1
    assert result.actual_carbs_g == 65


def test_never_undershoots():
    for target in range(1, 130, 5):
        result = select_gels(target)
        assert result.actual_carbs_g >= target, (
            f"target={target}: actual={result.actual_carbs_g} undershoots"
        )


def test_always_whole_gels():
    for target in range(0, 130, 5):
        result = select_gels(target)
        assert isinstance(result.n_large, int) and result.n_large >= 0
        assert isinstance(result.n_small, int) and result.n_small >= 0


def test_overshoot_is_consistent():
    for target in range(1, 130, 5):
        result = select_gels(target)
        assert result.overshoot_g == result.actual_carbs_g - target


def test_minimises_gel_count():
    """For every target, no fewer-gel combination could have worked."""
    L, S = 40, 25
    for target in range(1, 130, 5):
        result = select_gels(target)
        n_total = result.n_large + result.n_small
        # Check that n_total - 1 gels cannot reach the target
        if n_total > 1:
            max_with_fewer = (n_total - 1) * L
            assert max_with_fewer < target, (
                f"target={target}: {n_total-1} large gels ({max_with_fewer}g) "
                "could have met the target with fewer gels"
            )
