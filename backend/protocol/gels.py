"""Gel selection — variable-size, brand-aware.

Given a per-window carb target and a list of gel options available for the
chosen brand + ratio phase, picks the combination of whole gels that:

  1. Always meets or exceeds the target (never undershoots).
  2. Minimises the overshoot (actual - target).
  3. Tie-break: prefers more, smaller gels over fewer, larger ones —
     keeping per-bite carbs low and spreading intake.
"""
from collections import Counter
from itertools import combinations_with_replacement
from typing import List

from .models import GelEntry, GelOption, GelPackageItem, GelPackageSummary, Week


MAX_GELS_PER_WINDOW = 12   # hard ceiling on combo search; no real session needs more


def select_gels(target_carbs_g: int, options: List[GelOption]) -> List[GelEntry]:
    """Return the optimal multiset of gels meeting target.

    `options` is the catalogue available for this window (already filtered by
    brand + ratio_phase by the caller). Multiple options at the same carbs_g
    are deduplicated by carbs_g — only one product per size is used.
    """
    if target_carbs_g <= 0 or not options:
        return []

    # Deduplicate by carbs_g (prefer first occurrence — assumes caller passes
    # the preferred product first if there's a choice)
    options_by_size: dict[int, GelOption] = {}
    for opt in options:
        options_by_size.setdefault(opt.carbs_g, opt)

    sizes = sorted(options_by_size.keys())
    if not sizes:
        return []

    # Sanity: can we even reach the target within MAX_GELS_PER_WINDOW?
    if max(sizes) * MAX_GELS_PER_WINDOW < target_carbs_g:
        raise ValueError(
            f"Cannot meet {target_carbs_g}g target with up to {MAX_GELS_PER_WINDOW} "
            f"gels of available sizes {sizes}"
        )

    # Best is keyed (overshoot ASC, -count ASC) so the smaller overshoot wins,
    # and on ties the larger gel count (= more, smaller gels) wins.
    best_key = None
    best_combo: tuple[int, ...] = ()

    for n_total in range(1, MAX_GELS_PER_WINDOW + 1):
        for combo in combinations_with_replacement(sizes, n_total):
            total = sum(combo)
            if total < target_carbs_g:
                continue
            overshoot = total - target_carbs_g
            key = (overshoot, -n_total)
            if best_key is None or key < best_key:
                best_key = key
                best_combo = combo
                if overshoot == 0:
                    # Exact match found at this n_total — no point looking at
                    # larger combos: any larger combo will overshoot.
                    # But a *smaller* n_total with exact match would also have
                    # zero overshoot; n_total grows here, so we keep -n_total
                    # tie-break by continuing the inner loop only.
                    pass

    counts = Counter(best_combo)
    return [
        GelEntry(
            gel_id=options_by_size[c].id,
            brand=options_by_size[c].brand,
            product_name=options_by_size[c].product_name,
            carbs_g=c,
            size_label=options_by_size[c].size_label,
            quantity=q,
        )
        for c, q in sorted(counts.items())
    ]


def summarise_package(weeks: List[Week]) -> GelPackageSummary:
    """Tally all gels across the plan, grouped by product (gel_id)."""
    # Aggregate quantities per gel_id
    by_id: dict[str, GelPackageItem] = {}

    for week in weeks:
        for session in week.sessions:
            for window in session.fueling_windows:
                phase = _phase_from_ratio(window.gel_ratio)
                for entry in window.gels:
                    key = entry.gel_id
                    if key in by_id:
                        by_id[key].quantity += entry.quantity
                    else:
                        by_id[key] = GelPackageItem(
                            gel_id=entry.gel_id,
                            brand=entry.brand,
                            product_name=entry.product_name,
                            size_label=entry.size_label,
                            carbs_g=entry.carbs_g,
                            ratio_phase=phase,
                            quantity=entry.quantity,
                        )

    # Stable order: ratio_phase asc, then carbs_g asc, then brand
    items = sorted(by_id.values(), key=lambda i: (i.ratio_phase, i.carbs_g, i.brand))
    total = sum(i.quantity for i in items)
    return GelPackageSummary(items=items, total_gels=total)


def _phase_from_ratio(ratio):
    from .models import GelRatio
    if ratio == GelRatio.GLUCOSE_100:
        return 1
    if ratio == GelRatio.RATIO_2_1:
        return 2
    return 3
