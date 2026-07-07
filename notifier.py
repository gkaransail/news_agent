import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from twilio.rest import Client
from config import (
    GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, RECIPIENT_WHATSAPP,
)


def _build_html_email(digests: dict[str, str]) -> str:
    today = date.today().strftime("%A, %B %d, %Y")
    topic_blocks = ""
    for topic, content in digests.items():
        # Convert markdown bullets to HTML
        lines = content.split("\n")
        html_lines = []
        for line in lines:
            if line.startswith("- ") or line.startswith("• "):
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith("**") and line.endswith("**"):
                html_lines.append(f"<strong>{line[2:-2]}</strong>")
            elif line.strip() == "":
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p>{line}</p>")
        body = "\n".join(html_lines)
        topic_blocks += f"""
        <div style="margin-bottom:32px;">
          <h2 style="color:#1a1a2e;border-bottom:2px solid #e94560;padding-bottom:6px;">{topic}</h2>
          <div style="line-height:1.7;color:#333;">{body}</div>
        </div>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:680px;margin:auto;padding:20px;background:#f9f9f9;">
      <div style="background:#1a1a2e;padding:20px;border-radius:8px 8px 0 0;">
        <h1 style="color:#e94560;margin:0;">Daily Intelligence Brief</h1>
        <p style="color:#aaa;margin:4px 0 0;">{today}</p>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #ddd;">
        {topic_blocks}
        <hr style="border:none;border-top:1px solid #eee;">
        <p style="color:#999;font-size:12px;text-align:center;">
          Powered by Grok AI · Delivered daily at 10 AM
        </p>
      </div>
    </body></html>"""


def send_email(digests: dict[str, str]) -> None:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[Email] Skipped — Gmail credentials not configured.")
        return

    today = date.today().strftime("%b %d, %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Brief: AI & Crypto — {today}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL

    plain_text = "\n\n---\n\n".join(f"{k}\n{v}" for k, v in digests.items())
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(_build_html_email(digests), "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print(f"[Email] Sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"[Email] Error: {e}")


def send_whatsapp(digests: dict[str, str]) -> None:
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not RECIPIENT_WHATSAPP:
        print("[WhatsApp] Skipped — Twilio credentials not configured.")
        return

    today = date.today().strftime("%b %d")
    lines = [f"*Daily Brief — {today}*\n"]
    for topic, content in digests.items():
        # Extract just the bullet points for WhatsApp (keep it short)
        bullets = [l for l in content.split("\n") if l.startswith("- ") or l.startswith("• ")][:4]
        lines.append(f"*{topic}*")
        lines.extend(bullets)
        lines.append("")

    lines.append("_Full digest in your email_ ✉️")
    message_body = "\n".join(lines)

    # WhatsApp has a 1600-char limit
    if len(message_body) > 1550:
        message_body = message_body[:1550] + "...\n_See email for full digest_"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_FROM,
            to=RECIPIENT_WHATSAPP,
        )
        print(f"[WhatsApp] Sent to {RECIPIENT_WHATSAPP}")
    except Exception as e:
        print(f"[WhatsApp] Error: {e}")


def notify(digests: dict[str, str]) -> None:
    send_email(digests)
    send_whatsapp(digests)
