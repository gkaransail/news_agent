import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from twilio.rest import Client
from config import (
    GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, RECIPIENT_WHATSAPP,
)


def _md_to_html(text: str) -> str:
    """Convert a markdown digest block to HTML."""
    lines = text.split("\n")
    html_parts = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(("- ", "• ", "* ")):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item = stripped[2:]
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            item = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', item)
            html_parts.append(f"<li>{item}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            if not stripped:
                continue
            processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            processed = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', processed)
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                heading_text = stripped.lstrip("# ")
                html_parts.append(f"<h{level}>{heading_text}</h{level}>")
            else:
                html_parts.append(f"<p>{processed}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def _build_html_email(digests: dict[str, str]) -> str:
    today = date.today().strftime("%A, %B %d, %Y")
    topic_blocks = ""
    for topic, content in digests.items():
        body = _md_to_html(content)
        topic_blocks += f"""
        <div style="margin-bottom:32px;">
          <h2 style="color:#1a1a2e;border-bottom:2px solid #e94560;padding-bottom:6px;">{topic}</h2>
          <div style="line-height:1.75;color:#333;font-size:15px;">{body}</div>
        </div>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:680px;margin:auto;padding:20px;background:#f4f4f8;">
      <div style="background:#1a1a2e;padding:24px 28px;border-radius:8px 8px 0 0;">
        <h1 style="color:#e94560;margin:0;font-size:22px;letter-spacing:0.5px;">Daily Intelligence Brief</h1>
        <p style="color:#aaa;margin:6px 0 0;font-size:13px;">{today}</p>
      </div>
      <div style="background:#fff;padding:28px;border-radius:0 0 8px 8px;border:1px solid #ddd;border-top:none;">
        {topic_blocks}
        <hr style="border:none;border-top:1px solid #eee;margin-top:24px;">
        <p style="color:#bbb;font-size:11px;text-align:center;margin-top:12px;">
          Powered by Grok AI &nbsp;·&nbsp; Delivered daily at 10 AM
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


def _extract_whatsapp_section(topic: str, content: str) -> str:
    lines = content.split("\n")
    bullets = [l.strip() for l in lines if re.match(r"^[-•*] ", l.strip())][:4]
    takeaway = next(
        (l.strip() for l in lines if "takeaway" in l.lower() or "key" in l.lower()),
        ""
    )
    section = [f"*{topic}*"]
    section.extend(bullets)
    if takeaway:
        clean = re.sub(r"\*\*(.+?)\*\*", r"*\1*", takeaway)
        section.append(f"\n_{clean}_")
    return "\n".join(section)


def send_whatsapp(digests: dict[str, str]) -> None:
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not RECIPIENT_WHATSAPP:
        print("[WhatsApp] Skipped — Twilio credentials not configured.")
        return

    today = date.today().strftime("%b %d")
    lines = [f"*Daily Brief — {today}*\n"]
    for topic, content in digests.items():
        lines.append(_extract_whatsapp_section(topic, content))
        lines.append("")

    lines.append("_Full digest in your email_ ✉️")
    message_body = "\n".join(lines)

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
