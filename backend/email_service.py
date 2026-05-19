"""Transactional email delivery via Resend.

Env vars:
    RESEND_API_KEY    e.g. re_abc123...           (required)
    FROM_EMAIL        sender address              (required; until your domain
                                                   is verified in Resend, use
                                                   onboarding@resend.dev)
    FROM_NAME         display name in the From header (defaults to "TrainedGut")

If RESEND_API_KEY or FROM_EMAIL is missing, send is a no-op (logs and returns).
Plan generation itself must never fail because of an email problem.
"""
import base64
import os
from datetime import date

import resend

from protocol.models import GeneratePlanResponse


RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")
FROM_NAME = os.environ.get("FROM_NAME", "TrainedGut")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def _configured() -> bool:
    return bool(RESEND_API_KEY and FROM_EMAIL)


def _build_week_email_html(response: GeneratePlanResponse, week_number: int) -> str:
    plan = response.plan
    week = next((w for w in plan.weeks if w.week_number == week_number), None)
    if week is None:
        return _build_plan_email_html(response)

    # aggregate gels for this week
    by_key: dict = {}
    for s in week.sessions:
        for w in s.fueling_windows:
            for g in (w.gels or []):
                key = g.gel_id
                if key in by_key:
                    by_key[key]["quantity"] += g.quantity
                else:
                    by_key[key] = {
                        "name": g.product_name or f"{g.brand} {g.size_label}",
                        "carbs_g": g.carbs_g,
                        "quantity": g.quantity,
                    }
    total_gels = sum(v["quantity"] for v in by_key.values())
    gels_rows = "".join(
        f'<tr><td style="padding:8px 16px;font-size:13px;color:#1A1A14;border-bottom:1px solid #E2DDD4;">{v["name"]}</td>'
        f'<td style="padding:8px 16px;font-size:13px;color:#6B6B5E;border-bottom:1px solid #E2DDD4;text-align:right;">{v["carbs_g"]}g</td>'
        f'<td style="padding:8px 16px;font-size:13px;color:#1A1A14;font-weight:600;border-bottom:1px solid #E2DDD4;text-align:right;">{v["quantity"]}×</td></tr>'
        for v in by_key.values()
    )

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F5F0E8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1A1A14;line-height:1.6;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F5F0E8;padding:40px 20px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#FFFFFF;border-top:4px solid #E8521A;">
        <tr><td style="padding:32px 40px 8px;">
          <div style="font-size:13px;letter-spacing:0.18em;text-transform:uppercase;color:#E8521A;font-weight:600;">TrainedGut</div>
        </td></tr>
        <tr><td style="padding:8px 40px 16px;">
          <h1 style="margin:0;font-size:26px;line-height:1.2;color:#1A1A14;font-weight:600;">Week {week.week_number} of {plan.total_weeks}</h1>
          <p style="margin:8px 0 0;font-size:14px;color:#6B6B5E;">{week.start_date.isoformat()} - {week.end_date.isoformat()}</p>
        </td></tr>
        <tr><td style="padding:0 40px 24px;font-size:15px;color:#3A3A30;">
          <p style="margin:0 0 12px;">Target this week: <strong>{week.target_carbs_per_hour_g} g/hr</strong>{" - hold week" if week.is_consolidation else ""}.</p>
          <p style="margin:0 0 16px;">Full session-by-session details for the week are in the attached PDF.</p>
        </td></tr>
        <tr><td style="padding:0 40px 24px;">
          <p style="margin:0 0 8px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6B6B5E;">Gels for this week ({total_gels})</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2DDD4;">
            {gels_rows}
          </table>
        </td></tr>
        <tr><td style="padding:8px 40px 32px;" align="left">
          <a href="https://trainedgut.store" style="display:inline-block;background:#E8521A;color:#FFFFFF;text-decoration:none;padding:14px 32px;font-size:14px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">Open in app</a>
        </td></tr>
        <tr><td style="padding:0 40px;"><div style="height:1px;background:#E2DDD4;"></div></td></tr>
        <tr><td style="padding:24px 40px 32px;font-size:12px;color:#999;">- The TrainedGut team<br><a href="https://trainedgut.com" style="color:#999;text-decoration:none;">trainedgut.com</a></td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def _build_plan_email_html(response: GeneratePlanResponse) -> str:
    plan = response.plan
    days_to_race = (plan.race_date - date.today()).days
    countdown = (
        f"in {days_to_race} days"
        if days_to_race > 0
        else "race day" if days_to_race == 0
        else f"{-days_to_race} days ago"
    )

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Your TrainedGut plan is ready</title>
</head>
<body style="margin:0;padding:0;background:#F5F0E8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1A1A14;line-height:1.6;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F5F0E8;padding:40px 20px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#FFFFFF;border-top:4px solid #E8521A;">

          <tr>
            <td style="padding:32px 40px 8px;">
              <div style="font-size:13px;letter-spacing:0.18em;text-transform:uppercase;color:#E8521A;font-weight:600;">TrainedGut</div>
            </td>
          </tr>

          <tr>
            <td style="padding:8px 40px 16px;">
              <h1 style="margin:0;font-size:26px;line-height:1.2;color:#1A1A14;font-weight:600;letter-spacing:-0.01em;">Your plan is ready</h1>
              <p style="margin:8px 0 0;font-size:14px;color:#6B6B5E;">Race date: {plan.race_date.isoformat()} ({countdown})</p>
            </td>
          </tr>

          <tr>
            <td style="padding:0 40px 24px;font-size:15px;color:#3A3A30;">
              <p style="margin:0 0 16px;">
                The full week-by-week protocol is in the attached PDF - print it, put it on the fridge,
                or open it on your phone during a long session.
              </p>
            </td>
          </tr>

          <tr>
            <td style="padding:0 40px 24px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2DDD4;">
                <tr>
                  <td style="padding:12px 16px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6B6B5E;border-bottom:1px solid #E2DDD4;">Total weeks</td>
                  <td style="padding:12px 16px;font-size:14px;color:#1A1A14;font-weight:600;border-bottom:1px solid #E2DDD4;text-align:right;">{plan.total_weeks}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6B6B5E;border-bottom:1px solid #E2DDD4;">Starting intake</td>
                  <td style="padding:12px 16px;font-size:14px;color:#1A1A14;font-weight:600;border-bottom:1px solid #E2DDD4;text-align:right;">{plan.starting_carbs_per_hour_g} g/hr</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6B6B5E;border-bottom:1px solid #E2DDD4;">Peak target</td>
                  <td style="padding:12px 16px;font-size:14px;color:#1A1A14;font-weight:600;border-bottom:1px solid #E2DDD4;text-align:right;">{plan.race_target_carbs_per_hour_g} g/hr</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6B6B5E;">Total gels in package</td>
                  <td style="padding:12px 16px;font-size:14px;color:#1A1A14;font-weight:600;text-align:right;">{plan.gel_package.total_gels}</td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td style="padding:8px 40px 32px;" align="left">
              <a href="https://trainedgut.store"
                 style="display:inline-block;background:#E8521A;color:#FFFFFF;text-decoration:none;padding:14px 32px;font-size:14px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">
                Open in app
              </a>
            </td>
          </tr>

          <tr>
            <td style="padding:0 40px;">
              <div style="height:1px;background:#E2DDD4;"></div>
            </td>
          </tr>

          <tr>
            <td style="padding:24px 40px 32px;font-size:12px;color:#6B6B5E;line-height:1.6;">
              <p style="margin:0 0 8px;">
                You can log session feedback, mark sessions as skipped, and add unplanned sessions
                directly in the app. The PDF is your offline reference.
              </p>
              <p style="margin:16px 0 0;color:#999;">
                - The TrainedGut team<br>
                <a href="https://trainedgut.com" style="color:#999;text-decoration:none;">trainedgut.com</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_plan_email(
    to_email: str,
    response: GeneratePlanResponse,
    pdf_bytes: bytes,
    subject: str | None = None,
    week_number: int | None = None,
) -> None:
    """Send the plan email with PDF attached. Silently no-ops if SMTP not configured.

    If week_number is set, the body shows just that week's summary and the PDF
    attachment is named accordingly.
    """
    if not _configured():
        print("[email_service] Resend not configured (set RESEND_API_KEY + FROM_EMAIL), skipping email")
        return
    if not response.plan:
        return

    if subject is None:
        subject = (
            f"Your TrainedGut plan - Week {week_number}"
            if week_number is not None
            else "Your TrainedGut plan is ready"
        )

    html_body = (
        _build_week_email_html(response, week_number)
        if week_number is not None
        else _build_plan_email_html(response)
    )

    pdf_filename = (
        f"trainedgut-week-{week_number}.pdf"
        if week_number is not None
        else "trainedgut-plan.pdf"
    )

    print(f"[email_service] Attempting to send to {to_email} via Resend (from {FROM_EMAIL})")
    try:
        result = resend.Emails.send({
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "attachments": [{
                "filename": pdf_filename,
                "content": base64.b64encode(pdf_bytes).decode("ascii"),
            }],
        })
        print(f"[email_service] Plan email sent to {to_email} (resend id: {result.get('id')})")
    except Exception as e:
        print(f"[email_service] Failed to send plan email to {to_email}: {type(e).__name__}: {e}")
        raise
