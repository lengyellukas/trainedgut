"""Generate a printable PDF of an athlete's gut training plan.

Pure-Python (fpdf2), no system dependencies — deploys cleanly on Railway.
"""
from datetime import date
from typing import Iterable

from fpdf import FPDF

from protocol.models import GeneratePlanResponse, Plan, Week, Session, FuelingWindow

# Brand colours (RGB)
DARK = (26, 26, 20)
ORANGE = (232, 82, 26)
GOLD = (200, 150, 62)
GRAY = (107, 107, 94)
LIGHT_GRAY = (226, 221, 212)
WHITE = (253, 250, 245)


class _PlanPDF(FPDF):
    def header(self):
        # Slim brand bar at the top of every page
        self.set_fill_color(*DARK)
        self.rect(0, 0, self.w, 12, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.set_xy(10, 3)
        self.cell(0, 6, "TrainedGut", align="L")
        self.set_font("Helvetica", "", 8)
        self.set_xy(0, 4)
        self.cell(0, 4, "Personalised gut training plan", align="R")
        # leave space below header for content
        self.set_y(18)

    def footer(self):
        self.set_y(-12)
        self.set_text_color(*GRAY)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 6, f"Page {self.page_no()} / {{nb}}  -  trainedgut.com", align="C")


def _format_date(d: date) -> str:
    return d.strftime("%a, %d %b %Y")


def _format_date_short(d: date) -> str:
    return d.strftime("%a %d %b")


def _h2(pdf: FPDF, text: str) -> None:
    pdf.set_text_color(*ORANGE)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _h3(pdf: FPDF, text: str, color=DARK) -> None:
    pdf.set_text_color(*color)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")


def _label_value(pdf: FPDF, label: str, value: str) -> None:
    pdf.set_text_color(*GRAY)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(45, 5, label.upper(), new_x="RIGHT")
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")


def _build_cover(pdf: FPDF, response: GeneratePlanResponse) -> None:
    plan = response.plan
    days_to_race = (plan.race_date - date.today()).days

    _h2(pdf, "Your gut training plan")
    pdf.set_text_color(*GRAY)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"{plan.total_weeks} weeks - sport: {plan.sport_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    _label_value(pdf, "Race date", _format_date(plan.race_date))
    if days_to_race > 0:
        _label_value(pdf, "Days to race", f"{days_to_race}")
    elif days_to_race == 0:
        _label_value(pdf, "Days to race", "RACE DAY")
    _label_value(pdf, "Total weeks", f"{plan.total_weeks}")
    _label_value(pdf, "Starting", f"{plan.starting_carbs_per_hour_g} g/hr")
    _label_value(pdf, "Peak target", f"{plan.race_target_carbs_per_hour_g} g/hr")
    _label_value(pdf, "Body weight", f"{plan.athlete_body_weight_kg} kg")

    pdf.ln(6)
    pdf.set_draw_color(*LIGHT_GRAY)
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    pdf.ln(6)

    pdf.set_text_color(*GRAY)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0, 5,
        "The pages that follow contain your week-by-week protocol: every session, "
        "every fuelling window, every gel. The final page lists the complete gel "
        "package so you know exactly what to order or buy before you start.",
        new_x="LMARGIN", new_y="NEXT",
    )


def _build_week_block(pdf: FPDF, week: Week) -> None:
    # Page-break if not enough room
    if pdf.get_y() > 230:
        pdf.add_page()

    # Week header
    pdf.set_fill_color(*DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 12)
    label = f"Week {week.week_number}  -  {_format_date_short(week.start_date)} to {_format_date_short(week.end_date)}"
    if week.is_consolidation:
        label += "  -  HOLD WEEK"
    pdf.cell(0, 8, " " + label, fill=True, new_x="LMARGIN", new_y="NEXT")

    # Stats line
    pdf.set_fill_color(245, 245, 240)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9)
    stats = f"  Target: {week.target_carbs_per_hour_g} g/hr   |   Ratio: {week.gel_ratio.value}   |   Sessions: {len(week.sessions)}"
    pdf.cell(0, 6, stats, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for s in week.sessions:
        _build_session_block(pdf, s)
    pdf.ln(3)


def _build_session_block(pdf: FPDF, session: Session) -> None:
    pdf.set_text_color(*GOLD)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        0, 5,
        f"Session {session.session_number}  -  {session.duration_option}  -  "
        f"{session.n_fueling_windows} windows  -  {session.total_actual_carbs_g}g total",
        new_x="LMARGIN", new_y="NEXT",
    )

    # Table header
    pdf.set_text_color(*GRAY)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(20, 5, "TIME", border="B")
    pdf.cell(100, 5, "GELS", border="B")
    pdf.cell(25, 5, "TARGET", border="B")
    pdf.cell(25, 5, "ACTUAL", border="B", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9)
    for w in session.fueling_windows:
        gels_text = ", ".join(
            f"{g.quantity}x {g.product_name or (g.brand + ' ' + g.size_label)} ({g.carbs_g}g)"
            for g in (w.gels or [])
        ) or "-"
        actual = f"{w.actual_carbs_g}g"
        if w.overshoot_g > 0:
            actual += f" (+{w.overshoot_g})"
        pdf.cell(20, 5, f"T+{w.time_from_start_minutes}")
        pdf.cell(100, 5, gels_text[:60])   # truncate so it doesn't overflow
        pdf.cell(25, 5, f"{w.target_carbs_g}g")
        pdf.cell(25, 5, actual, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _build_package_page(pdf: FPDF, plan: Plan) -> None:
    pdf.add_page()
    _h2(pdf, "Complete gel package")
    pdf.set_text_color(*GRAY)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0, 5,
        "This is the total quantity of each product needed across the full plan. "
        "Order or buy these before week 1 begins.",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(4)

    phase_label = {
        1: "Phase 1 - 100% glucose",
        2: "Phase 2 - 2:1 (glucose:fructose)",
        3: "Phase 3 - 1:0.8 (glucose:fructose)",
    }

    grouped: dict[int, list] = {1: [], 2: [], 3: []}
    for item in plan.gel_package.items:
        grouped.setdefault(item.ratio_phase, []).append(item)

    for phase in (1, 2, 3):
        items = grouped.get(phase) or []
        if not items:
            continue
        _h3(pdf, phase_label[phase], color=GOLD)
        pdf.set_text_color(*GRAY)
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(90, 5, "PRODUCT", border="B")
        pdf.cell(30, 5, "CARBS", border="B")
        pdf.cell(30, 5, "QUANTITY", border="B", new_x="LMARGIN", new_y="NEXT")

        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "", 10)
        for item in items:
            label = item.product_name or f"{item.brand} {item.size_label}"
            pdf.cell(90, 6, label)
            pdf.cell(30, 6, f"{item.carbs_g}g per gel")
            pdf.cell(30, 6, f"{item.quantity} x", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    pdf.set_draw_color(*LIGHT_GRAY)
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    pdf.ln(4)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, f"Total gels in plan: {plan.gel_package.total_gels}", new_x="LMARGIN", new_y="NEXT")


def generate_plan_pdf(response: GeneratePlanResponse, week_number: int | None = None) -> bytes:
    """Render a PDF of the plan. Pass `week_number` to render only that week.

    Full PDF: cover + all weeks + package shopping list.
    Single-week PDF: lightweight one-week handout (header + that week's block).
    """
    if not response.plan:
        raise ValueError("Cannot build PDF for a response without a plan")

    pdf = _PlanPDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(10, 18, 10)
    pdf.add_page()

    if week_number is None:
        _build_cover(pdf, response)
        pdf.add_page()
        _h2(pdf, "Week-by-week protocol")
        pdf.ln(2)
        for week in response.plan.weeks:
            _build_week_block(pdf, week)
        _build_package_page(pdf, response.plan)
    else:
        target_week = next((w for w in response.plan.weeks if w.week_number == week_number), None)
        if not target_week:
            raise ValueError(f"Week {week_number} not in this plan")
        _h2(pdf, f"Week {target_week.week_number} of {response.plan.total_weeks}")
        pdf.set_text_color(*GRAY)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"{_format_date(target_week.start_date)} to {_format_date(target_week.end_date)}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        _build_week_block(pdf, target_week)

    return bytes(pdf.output())
