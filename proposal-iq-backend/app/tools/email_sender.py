"""
Email node: sends the generated report via Resend (https://resend.com).

Why Resend instead of an internal SMTP server:
- Free tier (3,000/month, 100/day) is far more than a 5-day sprint needs
- Simple HTTPS API call, no SMTP host/port/credential wrangling
- Works from anywhere without VPN/network access to a company mail server

Setup: sign up at resend.com, create an API key, put it in .env as
RESEND_API_KEY. FROM_EMAIL defaults to Resend's shared test sender
(onboarding@resend.dev), which works immediately but may be flagged as spam
by strict inboxes — verify your own domain in Resend's dashboard for the
real demo if that matters.
"""
import resend

from proposal_iq.config import RESEND_API_KEY, FROM_EMAIL
from proposal_iq.tools.report import html_to_pdf_bytes


def send_report_email(to_email: str, company_name: str, report_html: str) -> dict:
    if not RESEND_API_KEY:
        return {
            "sent": False,
            "error": "RESEND_API_KEY is not set. Add it to your .env file.",
        }

    resend.api_key = RESEND_API_KEY
    pdf_bytes = html_to_pdf_bytes(report_html)
    safe_name = "".join(c if c.isalnum() else "_" for c in company_name).strip("_")

    try:
        resend.Emails.send(
            {
                "from": FROM_EMAIL,
                "to": [to_email],
                "subject": f"Opportunity Report — {company_name}",
                "html": report_html,
                "attachments": [
                    {
                        "filename": f"{safe_name}_report.pdf",
                        "content": list(pdf_bytes),
                    }
                ],
            }
        )
        return {"sent": True, "error": None}
    except Exception as e:
        return {"sent": False, "error": f"Resend send failed: {e}"}