from datetime import date

from sqlalchemy.orm import Session, joinedload
from protocol.models import (
    Plan, GelRatio, GeneratePlanResponse, PlanStatus,
    Plan as PlanResponse, Week as WeekResponse,
    Session as SessionResponse, FuelingWindow as FuelingWindowResponse,
    GelOption, GelEntry, GelPackageItem, GelPackageSummary,
)
from protocol.inputs import AthleteProfile
from models_db import Athlete, Plan as PlanDB, Week, Session as SessionDB, FuelingWindow, FuelingWindowGel, Gel, Feedback, ExtraSession

GEL_RATIO_TO_PHASE = {
    GelRatio.GLUCOSE_100: 1,
    GelRatio.RATIO_2_1:   2,
    GelRatio.RATIO_1_08:  3,
}

PHASE_TO_GEL_RATIO = {v: k for k, v in GEL_RATIO_TO_PHASE.items()}


def find_or_create_athlete(db: Session, email: str, supabase_user_id: str | None = None) -> Athlete:
    """Look up an athlete by Supabase user id (preferred) or email; create if missing."""
    athlete = None
    if supabase_user_id:
        athlete = db.query(Athlete).filter(Athlete.supabase_user_id == supabase_user_id).first()
    if not athlete:
        athlete = db.query(Athlete).filter(Athlete.email == email).first()

    if not athlete:
        athlete = Athlete(email=email, supabase_user_id=supabase_user_id)
        db.add(athlete)
        db.commit()
        db.refresh(athlete)
    elif supabase_user_id and not athlete.supabase_user_id:
        # Backfill the supabase user id on an existing email-only row
        athlete.supabase_user_id = supabase_user_id
        db.commit()

    return athlete


def _get_or_create_athlete(db: Session, email: str, supabase_user_id: str | None, profile: AthleteProfile) -> Athlete:
    athlete = find_or_create_athlete(db, email, supabase_user_id)
    # Update biometric fields from the latest plan submission
    athlete.birth_year = getattr(profile, "birth_year", None) or athlete.birth_year
    athlete.weight_kg = profile.body_weight_kg
    athlete.height_cm = getattr(profile, "height_cm", None) or athlete.height_cm
    db.flush()
    return athlete


def load_gel_options(db: Session, brand: str, market: str | None = None) -> list[GelOption]:
    """Return gel options for the chosen source.

    brand='trainedgut'  → only TrainedGut catalogue
    brand='third_party' → all brands except TrainedGut (mix and match)
    """
    q = db.query(Gel)
    if brand == "trainedgut":
        q = q.filter(Gel.brand == "trainedgut")
    elif brand == "third_party":
        q = q.filter(Gel.brand != "trainedgut")
    rows = q.all()
    if market:
        rows = [r for r in rows if market in (r.markets or [])]
    return [
        GelOption(
            id=g.id,
            brand=g.brand,
            product_name=g.product_name,
            carbs_g=g.carbs_g,
            size_label=g.size,
            ratio_phase=g.ratio_phase,
        )
        for g in rows
    ]


def save_plan(db: Session, email: str, supabase_user_id: str | None, profile: AthleteProfile, plan: Plan) -> PlanDB:
    athlete = _get_or_create_athlete(db, email, supabase_user_id, profile)

    weeks = plan.weeks
    db_plan = PlanDB(
        athlete_id=athlete.id,
        sport_type=profile.sport_type.value,
        race_date=profile.race_date,
        target_race_time_hours=profile.target_race_time_hours,
        start_preference=profile.start_preference.value,
        preferred_start_date=profile.preferred_start_date,
        long_sessions=[{"duration_option": s.duration_option.value} for s in profile.long_sessions],
        carb_tolerance=profile.carb_tolerance_option.value,
        gi_history=profile.gi_history.value,
        start_date=weeks[0].start_date,
        end_date=weeks[-1].end_date,
        is_active=True,
    )
    db.add(db_plan)
    db.flush()

    for week in weeks:
        phase = GEL_RATIO_TO_PHASE[week.gel_ratio]
        db_week = Week(
            plan_id=db_plan.id,
            week_number=week.week_number,
            start_date=week.start_date,
            end_date=week.end_date,
            target_carbs_g_per_hour=week.target_carbs_per_hour_g,
            ratio_phase=phase,
            is_consolidation=week.is_consolidation,
        )
        db.add(db_week)
        db.flush()

        for session in week.sessions:
            db_session = SessionDB(
                week_id=db_week.id,
                session_number=session.session_number,
                duration_option=session.duration_option,
                n_fueling_windows=session.n_fueling_windows,
            )
            db.add(db_session)
            db.flush()

            for window in session.fueling_windows:
                db_window = FuelingWindow(
                    session_id=db_session.id,
                    window_number=window.window_number,
                    time_minutes=window.time_from_start_minutes,
                    carbs_target_g=window.target_carbs_g,
                    carbs_actual_g=window.actual_carbs_g,
                )
                db.add(db_window)
                db.flush()
                for entry in window.gels:
                    db.add(FuelingWindowGel(
                        window_id=db_window.id,
                        gel_id=entry.gel_id,
                        quantity=entry.quantity,
                    ))

    db.commit()
    return db_plan


def _resolve_week(db: Session, supabase_user_id: str, week_number: int) -> Week | None:
    athlete = db.query(Athlete).filter(Athlete.supabase_user_id == supabase_user_id).first()
    if not athlete:
        return None

    plan = (
        db.query(PlanDB)
        .filter(PlanDB.athlete_id == athlete.id, PlanDB.is_active == True)
        .order_by(PlanDB.created_at.desc())
        .first()
    )
    if not plan:
        return None

    return db.query(Week).filter(Week.plan_id == plan.id, Week.week_number == week_number).first()


def save_feedback(
    db: Session,
    supabase_user_id: str,
    week_number: int,
    session_number: int,
    status: str,
    consumed_vs_plan: str | None,
    consumed_ratio: float | None,
    gi_scale: int | None,
) -> Feedback | None:
    week = _resolve_week(db, supabase_user_id, week_number)
    if not week:
        return None

    session = db.query(SessionDB).filter(
        SessionDB.week_id == week.id,
        SessionDB.session_number == session_number,
    ).first()
    if not session:
        return None

    feedback = Feedback(
        session_id=session.id,
        status=status,
        consumed_vs_plan=consumed_vs_plan,
        consumed_ratio=consumed_ratio,
        gi_scale=gi_scale,
    )
    db.add(feedback)
    db.commit()
    return feedback


def save_extra_session(
    db: Session,
    supabase_user_id: str,
    week_number: int,
    duration_option: str,
    n_small_gels_consumed: int,
    n_large_gels_consumed: int,
    gi_scale: int,
) -> ExtraSession | None:
    week = _resolve_week(db, supabase_user_id, week_number)
    if not week:
        return None

    extra = ExtraSession(
        week_id=week.id,
        duration_option=duration_option,
        n_small_gels_consumed=n_small_gels_consumed,
        n_large_gels_consumed=n_large_gels_consumed,
        gi_scale=gi_scale,
    )
    db.add(extra)
    db.commit()
    return extra


def delete_active_plan(db: Session, supabase_user_id: str) -> bool:
    """Delete the user's currently active plan (and all cascaded children). Returns True if deleted."""
    athlete = db.query(Athlete).filter(Athlete.supabase_user_id == supabase_user_id).first()
    if not athlete:
        return False

    plan = (
        db.query(PlanDB)
        .filter(PlanDB.athlete_id == athlete.id, PlanDB.is_active == True)
        .order_by(PlanDB.created_at.desc())
        .first()
    )
    if not plan:
        return False

    db.delete(plan)
    db.commit()
    return True


def list_extra_sessions(db: Session, supabase_user_id: str) -> list[dict]:
    """Return all extra sessions for the user's active plan, with week_number resolved."""
    athlete = db.query(Athlete).filter(Athlete.supabase_user_id == supabase_user_id).first()
    if not athlete:
        return []

    plan = (
        db.query(PlanDB)
        .filter(PlanDB.athlete_id == athlete.id, PlanDB.is_active == True)
        .order_by(PlanDB.created_at.desc())
        .first()
    )
    if not plan:
        return []

    rows = (
        db.query(ExtraSession, Week.week_number)
        .join(Week, ExtraSession.week_id == Week.id)
        .filter(Week.plan_id == plan.id)
        .order_by(ExtraSession.submitted_at)
        .all()
    )

    return [
        {
            "id": es.id,
            "week_number": week_number,
            "duration_option": es.duration_option,
            "n_small_gels_consumed": es.n_small_gels_consumed,
            "n_large_gels_consumed": es.n_large_gels_consumed,
            "gi_scale": es.gi_scale,
            "submitted_at": es.submitted_at.isoformat(),
        }
        for es, week_number in rows
    ]


def load_active_plan_response(db: Session, supabase_user_id: str) -> GeneratePlanResponse | None:
    """Reconstruct the full GeneratePlanResponse for the user's active plan from DB tables."""
    athlete = db.query(Athlete).filter(Athlete.supabase_user_id == supabase_user_id).first()
    if not athlete:
        return None

    plan_db = (
        db.query(PlanDB)
        .filter(PlanDB.athlete_id == athlete.id, PlanDB.is_active == True)
        .order_by(PlanDB.created_at.desc())
        .first()
    )
    if not plan_db:
        return None

    # Eager-load weeks → sessions → fueling_windows → gel_entries → gel in one tree
    weeks_db = (
        db.query(Week)
        .filter(Week.plan_id == plan_db.id)
        .options(
            joinedload(Week.sessions)
            .joinedload(SessionDB.fueling_windows)
            .joinedload(FuelingWindow.gel_entries)
            .joinedload(FuelingWindowGel.gel)
        )
        .order_by(Week.week_number)
        .all()
    )
    if not weeks_db:
        return None

    weeks_response: list[WeekResponse] = []
    package_items: dict[str, GelPackageItem] = {}   # keyed by gel_id

    for week_db in weeks_db:
        gel_ratio = PHASE_TO_GEL_RATIO[week_db.ratio_phase]
        sessions_sorted = sorted(week_db.sessions, key=lambda s: s.session_number)

        sessions_response: list[SessionResponse] = []
        for s_db in sessions_sorted:
            windows_sorted = sorted(s_db.fueling_windows, key=lambda w: w.window_number)

            windows_response: list[FuelingWindowResponse] = []
            for w in windows_sorted:
                gel_entries_response: list[GelEntry] = []
                for je in w.gel_entries:
                    gel_entries_response.append(GelEntry(
                        gel_id=je.gel_id,
                        brand=je.gel.brand,
                        product_name=je.gel.product_name,
                        carbs_g=je.gel.carbs_g,
                        size_label=je.gel.size,
                        quantity=je.quantity,
                    ))
                    # accumulate package summary
                    key = je.gel_id
                    if key in package_items:
                        package_items[key].quantity += je.quantity
                    else:
                        package_items[key] = GelPackageItem(
                            gel_id=je.gel_id,
                            brand=je.gel.brand,
                            product_name=je.gel.product_name,
                            size_label=je.gel.size,
                            carbs_g=je.gel.carbs_g,
                            ratio_phase=je.gel.ratio_phase,
                            quantity=je.quantity,
                        )
                gel_count = sum(e.quantity for e in gel_entries_response)
                actual = int(w.carbs_actual_g)
                target = int(w.carbs_target_g)
                windows_response.append(FuelingWindowResponse(
                    window_number=w.window_number,
                    time_from_start_minutes=w.time_minutes,
                    target_carbs_g=target,
                    actual_carbs_g=actual,
                    overshoot_g=actual - target,
                    gel_count=gel_count,
                    gels=gel_entries_response,
                    gel_ratio=gel_ratio,
                ))

            sessions_response.append(SessionResponse(
                session_number=s_db.session_number,
                duration_option=s_db.duration_option,
                n_fueling_windows=s_db.n_fueling_windows,
                carbs_per_hour_g=int(week_db.target_carbs_g_per_hour),
                total_target_carbs_g=int(sum(w.carbs_target_g for w in windows_sorted)),
                total_actual_carbs_g=int(sum(w.carbs_actual_g for w in windows_sorted)),
                fueling_windows=windows_response,
            ))

        weeks_response.append(WeekResponse(
            week_number=week_db.week_number,
            start_date=week_db.start_date,
            end_date=week_db.end_date,
            target_carbs_per_hour_g=int(week_db.target_carbs_g_per_hour),
            gel_ratio=gel_ratio,
            is_consolidation=week_db.is_consolidation,
            sessions=sessions_response,
        ))

    items_sorted = sorted(package_items.values(), key=lambda i: (i.ratio_phase, i.carbs_g, i.brand))
    gel_package = GelPackageSummary(items=items_sorted, total_gels=sum(i.quantity for i in items_sorted))

    plan_response = PlanResponse(
        athlete_body_weight_kg=athlete.weight_kg or 0.0,
        sport_type=plan_db.sport_type,
        race_date=plan_db.race_date,
        starting_carbs_per_hour_g=int(weeks_db[0].target_carbs_g_per_hour),
        race_target_carbs_per_hour_g=max(int(w.target_carbs_g_per_hour) for w in weeks_db),
        total_weeks=len(weeks_db),
        weeks=weeks_response,
        gel_package=gel_package,
    )

    # Status: starts_late if start date hasn't arrived yet, else valid
    today = date.today()
    if plan_db.start_date > today:
        status = PlanStatus.STARTS_LATE
        message = f"Your plan starts on {plan_db.start_date.isoformat()}."
    else:
        status = PlanStatus.VALID
        message = ""

    return GeneratePlanResponse(status=status, status_message=message, plan=plan_response)
