"""SMTP email delivery for plan generation + future transactional emails.

SMTP credentials come from env vars:
    SMTP_HOST       e.g. smtp.websupport.sk
    SMTP_PORT       e.g. 465 (SSL) or 587 (STARTTLS)
    SMTP_USER       full mailbox address, e.g. join@trainedgut.com
    SMTP_PASSWORD   mailbox password
    FROM_EMAIL      optional override for the From: header (defaults to SMTP_USER)
    FROM_NAME       optional display name (defaults to "TrainedGut")

If any required var is missing, send is a no-op (logs and returns). Plan
generation itself must never fail because of an email problem.
"""
import os
import smtplib
import ssl
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from protocol.models import GeneratePlanResponse


SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.environ.get("FROM_NAME", "TrainedGut")


def _smtp_configured() -> bool:
    return all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL])


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


def send_plan_email(to_email: str, response: GeneratePlanResponse, pdf_bytes: bytes, subject: str = "Your TrainedGut plan is ready") -> None:
    """Send the plan email with PDF attached. Silently no-ops if SMTP not configured."""
    if not _smtp_configured():
        print("[email_service] SMTP not configured, skipping plan email")
        return
    if not response.plan:
        return

    msg = MIMEMultipart()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    html_body = _build_plan_email_html(response)
    msg.attach(MIMEText(html_body, "html", _charset="utf-8"))

    pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_part.add_header("Content-Disposition", "attachment", filename="trainedgut-plan.pdf")
    msg.attach(pdf_part)

    context = ssl.create_default_context()
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
                smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls(context=context)
                smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
        print(f"[email_service] Plan email sent to {to_email}")
    except Exception as e:
        print(f"[email_service] Failed to send plan email to {to_email}: {e}")
