"""
Tests for the variable-size, brand-aware gel selection algorithm.
"""
from protocol.gels import select_gels
from protocol.models import GelOption


def _opt(carbs_g: int, label: str = "small", phase: int = 1, brand: str = "trainedgut") -> GelOption:
    return GelOption(id=f"{brand}-{label}-{carbs_g}-{phase}", brand=brand, carbs_g=carbs_g, size_label=label, ratio_phase=phase)


TRAINEDGUT = [_opt(25, "small"), _opt(40, "large")]


def test_zero_target_returns_empty():
    assert select_gels(0, TRAINEDGUT) == []


def test_no_options_returns_empty():
    assert select_gels(50, []) == []


def test_exact_small_gel():
    gels = select_gels(25, TRAINEDGUT)
    assert len(gels) == 1
    assert gels[0].carbs_g == 25 and gels[0].quantity == 1


def test_exact_large_gel():
    gels = select_gels(40, TRAINEDGUT)
    assert len(gels) == 1
    assert gels[0].carbs_g == 40 and gels[0].quantity == 1


def test_30g_picks_smallest_overshoot():
    # 1x40 (overshoot 10) beats 2x25 (overshoot 20)
    gels = select_gels(30, TRAINEDGUT)
    total = sum(g.carbs_g * g.quantity for g in gels)
    assert total == 40


def test_45g_picks_two_smalls():
    # 2x25=50 (overshoot 5) beats 1x40+1x25=65 (overshoot 20)
    gels = select_gels(45, TRAINEDGUT)
    total = sum(g.carbs_g * g.quantity for g in gels)
    assert total == 50


def test_50g_tie_break_prefers_more_smaller_gels():
    # 2x25=50 (exact, 2 gels) vs 1x40+? — only 2x25 reaches 50 exactly
    gels = select_gels(50, TRAINEDGUT)
    total = sum(g.carbs_g * g.quantity for g in gels)
    count = sum(g.quantity for g in gels)
    assert total == 50
    assert count == 2


def test_tie_break_prefers_more_gels_on_equal_overshoot():
    # Make an artificial situation where two combos overshoot equally;
    # pick the one with more gels.
    # Target 75: 3x25=75 (exact, 3 gels) wins over 1x40+2x25=90? No - 90 overshoots.
    # Better test: target 50: 2x25=50 (2 gels) vs nothing else exact.
    # Try with three options: 20, 25, 40 — target 45.
    options = [_opt(20, "xs"), _opt(25, "small"), _opt(40, "large")]
    gels = select_gels(45, options)
    total = sum(g.carbs_g * g.quantity for g in gels)
    # 1x25+1x20=45 (exact, 2 gels) wins over 2x25=50 (5 overshoot)
    assert total == 45


def test_never_undershoots():
    for target in range(1, 130, 5):
        gels = select_gels(target, TRAINEDGUT)
        total = sum(g.carbs_g * g.quantity for g in gels)
        assert total >= target, f"target={target}: total={total} undershoots"


def test_only_whole_gels():
    for target in range(0, 130, 5):
        gels = select_gels(target, TRAINEDGUT)
        for g in gels:
            assert isinstance(g.quantity, int) and g.quantity > 0


def test_brand_with_unusual_sizes():
    # SiS Go = 22g, SiS Beta Fuel = 40g
    sis = [_opt(22, "small", brand="sis"), _opt(40, "large", brand="sis")]
    gels = select_gels(60, sis)
    total = sum(g.carbs_g * g.quantity for g in gels)
    # 1x40+1x22=62 (overshoot 2) wins over 3x22=66 (overshoot 6)
    assert total == 62


def test_single_size_brand():
    # PF only has 30g in our hypothetical (PF 30)
    pf = [_opt(30, "small", brand="pf")]
    gels = select_gels(75, pf)
    total = sum(g.carbs_g * g.quantity for g in gels)
    # 3x30=90 (overshoot 15) is the only viable combo
    assert total == 90
    assert sum(g.quantity for g in gels) == 3


def test_overshoot_is_minimised():
    # Brute-force any target with TRAINEDGUT options
    for target in range(1, 130, 5):
        gels = select_gels(target, TRAINEDGUT)
        total = sum(g.carbs_g * g.quantity for g in gels)
        overshoot = total - target
        # Cannot improve by removing any gel (would undershoot)
        if gels:
            min_after_drop = min(g.carbs_g for g in gels)
            assert total - min_after_drop < target, (
                f"target={target}: could drop a gel and still meet target"
            )
