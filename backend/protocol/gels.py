import math
from dataclasses import dataclass
from typing import List

from . import config
from .models import GelPackageSummary, GelRatio, Week


@dataclass
class GelSelection:
    n_large: int          # 40g gels
    n_small: int          # 25g gels
    actual_carbs_g: int
    overshoot_g: int


def select_gels(target_carbs_g: int) -> GelSelection:
    """Find minimum whole gels meeting or exceeding target_carbs_g.

    For a given total gel count, picks the fewest large gels needed so the
    overshoot is minimised. Always overshoots — never half gels.
    """
    if target_carbs_g <= 0:
        return GelSelection(0, 0, 0, 0)

    L = config.LARGE_GEL_CARBS_G   # 40
    S = config.SMALL_GEL_CARBS_G   # 25

    for n_total in range(1, 20):
        # Minimum large gels for n_total gels to reach the target:
        # n_large * L + (n_total - n_large) * S >= target
        # n_large * (L - S) >= target - n_total * S
        n_large = max(0, math.ceil((target_carbs_g - n_total * S) / (L - S)))
        if n_large <= n_total:
            n_small = n_total - n_large
            actual = n_large * L + n_small * S
            return GelSelection(n_large, n_small, actual, actual - target_carbs_g)

    raise ValueError(f"Cannot satisfy {target_carbs_g}g target with up to 19 gels")


def summarise_package(weeks: List[Week]) -> GelPackageSummary:
    """Tally all gels across the plan, grouped by phase and size."""
    counts = {
        GelRatio.GLUCOSE_100: {"small": 0, "large": 0},
        GelRatio.RATIO_2_1: {"small": 0, "large": 0},
        GelRatio.RATIO_1_08: {"small": 0, "large": 0},
    }

    for week in weeks:
        for session in week.sessions:
            for window in session.fueling_windows:
                counts[window.gel_ratio]["large"] += window.n_large_gels
                counts[window.gel_ratio]["small"] += window.n_small_gels

    r1, r2, r3 = GelRatio.GLUCOSE_100, GelRatio.RATIO_2_1, GelRatio.RATIO_1_08
    total = sum(counts[r]["large"] + counts[r]["small"] for r in [r1, r2, r3])

    return GelPackageSummary(
        small_phase1_count=counts[r1]["small"],
        large_phase1_count=counts[r1]["large"],
        small_phase2_count=counts[r2]["small"],
        large_phase2_count=counts[r2]["large"],
        small_phase3_count=counts[r3]["small"],
        large_phase3_count=counts[r3]["large"],
        total_gels=total,
    )
