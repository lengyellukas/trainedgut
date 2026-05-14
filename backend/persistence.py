from sqlalchemy.orm import Session
from protocol.models import Plan, GelRatio
from protocol.inputs import AthleteProfile
from models_db import Athlete, Plan as PlanDB, Week, Session as SessionDB, FuelingWindow, Gel, Feedback, ExtraSession

GEL_RATIO_TO_PHASE = {
    GelRatio.GLUCOSE_100: 1,
    GelRatio.RATIO_2_1:   2,
    GelRatio.RATIO_1_08:  3,
}


def _get_or_create_athlete(db: Session, email: str, profile: AthleteProfile) -> Athlete:
    athlete = db.query(Athlete).filter(Athlete.email == email).first()
    if not athlete:
        athlete = Athlete(
            email=email,
            age=getattr(profile, "age", None),
            weight_kg=profile.body_weight_kg,
            height_cm=getattr(profile, "height_cm", None),
        )
        db.add(athlete)
        db.flush()
    return athlete


def _get_gel(db: Session, size: str, ratio_phase: int) -> Gel:
    return db.query(Gel).filter(Gel.size == size, Gel.ratio_phase == ratio_phase).one()


def save_plan(db: Session, email: str, profile: AthleteProfile, plan: Plan) -> PlanDB:
    athlete = _get_or_create_athlete(db, email, profile)

    gel_cache: dict[tuple, Gel] = {}
    def get_gel(size: str, phase: int) -> Gel:
        key = (size, phase)
        if key not in gel_cache:
            gel_cache[key] = _get_gel(db, size, phase)
        return gel_cache[key]

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
                small_gel = get_gel("small", phase) if window.n_small_gels > 0 else None
                large_gel = get_gel("large", phase) if window.n_large_gels > 0 else None
                db_window = FuelingWindow(
                    session_id=db_session.id,
                    small_gel_id=small_gel.id if small_gel else None,
                    large_gel_id=large_gel.id if large_gel else None,
                    window_number=window.window_number,
                    time_minutes=window.time_from_start_minutes,
                    carbs_target_g=window.target_carbs_g,
                    carbs_actual_g=window.actual_carbs_g,
                    n_small_gels=window.n_small_gels,
                    n_large_gels=window.n_large_gels,
                )
                db.add(db_window)

    db.commit()
    return db_plan


def _resolve_week(db: Session, email: str, week_number: int) -> Week | None:
    athlete = db.query(Athlete).filter(Athlete.email == email).first()
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
    email: str,
    week_number: int,
    session_number: int,
    status: str,
    consumed_vs_plan: str | None,
    consumed_ratio: float | None,
    gi_scale: int | None,
) -> Feedback | None:
    week = _resolve_week(db, email, week_number)
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
    email: str,
    week_number: int,
    duration_option: str,
    n_small_gels_consumed: int,
    n_large_gels_consumed: int,
    gi_scale: int,
) -> ExtraSession | None:
    week = _resolve_week(db, email, week_number)
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
