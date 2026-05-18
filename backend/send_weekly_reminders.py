"""
Sunday-evening weekly reminder — sends every athlete with an active plan
the per-week email + PDF for the week starting tomorrow (the upcoming Monday).

Reuses the existing single-week email pipeline (generate_plan_pdf + send_plan_email),
so the format matches what users get when they manually click "Email me this week".

Skipped:
- Athletes with no Supabase user id (won't happen for real users, but defensive)
- Athletes with no active plan (already done / cancelled)
- Plans where no week starts on the target Monday (plan hasn't reached its
  first full week yet, or has already ended)

Run manually:
    ./venv/bin/python send_weekly_reminders.py

Run on schedule (Sunday evening EU time): via the /admin/cron/weekly-reminders
endpoint triggered by GitHub Actions — see .github/workflows/weekly-reminders.yml.
"""
from datetime import date, timedelta

from database import SessionLocal
from models_db import Athlete, Plan as PlanDB
from persistence import load_active_plan_response
from pdf_generator import generate_plan_pdf
from email_service import send_plan_email


def _upcoming_monday(today: date) -> date:
    """Date of the next Monday (strictly in the future)."""
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7   # today is Monday → next Monday is in 7 days
    return today + timedelta(days=days_ahead)


def send_weekly_reminders(today: date | None = None) -> dict:
    today = today or date.today()
    target_monday = _upcoming_monday(today)

    db = SessionLocal()
    sent = skipped = errors = 0
    try:
        athletes = (
            db.query(Athlete)
            .join(PlanDB, PlanDB.athlete_id == Athlete.id)
            .filter(PlanDB.is_active == True)
            .distinct()
            .all()
        )
        for athlete in athletes:
            if not athlete.supabase_user_id:
                skipped += 1
                continue

            response = load_active_plan_response(db, supabase_user_id=athlete.supabase_user_id)
            if not response or not response.plan:
                skipped += 1
                continue

            target_week = next(
                (w for w in response.plan.weeks if w.start_date == target_monday),
                None,
            )
            if target_week is None:
                # No week in this plan starts on the target Monday
                # (plan ended, hasn't started yet, or first week is partial / non-Monday start)
                skipped += 1
                continue

            try:
                pdf_bytes = generate_plan_pdf(response, week_number=target_week.week_number)
                send_plan_email(
                    athlete.email,
                    response,
                    pdf_bytes,
                    subject=f"Your week ahead - Week {target_week.week_number}",
                    week_number=target_week.week_number,
                )
                sent += 1
            except Exception as exc:
                print(f"[weekly] Failed for {athlete.email}: {exc}")
                errors += 1
    finally:
        db.close()

    print(f"[weekly] target_monday={target_monday.isoformat()} sent={sent} skipped={skipped} errors={errors}")
    return {"target_monday": target_monday.isoformat(), "sent": sent, "skipped": skipped, "errors": errors}


if __name__ == "__main__":
    send_weekly_reminders()
