"""Service Notifications V3 — Email notifications."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from ..config import settings

logger = logging.getLogger(__name__)


async def send_video_ready_email(
    user_email: str,
    video_title: str,
    project_name: str,
    video_url: str = "",
) -> bool:
    """Envoie un email quand une vidéo est prête."""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.info(f"SMTP non configuré, notification ignorée pour {user_email}")
        return False

    subject = f"🎬 Reetik — Votre vidéo est prête !"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
        <h1 style="color: white; margin: 0;">🎬 Reetik</h1>
        <p style="color: rgba(255,255,255,0.9); margin-top: 5px;">Votre vidéo est prête !</p>
      </div>
      <div style="padding: 30px; background: #f8f9fa;">
        <h2 style="color: #333;">Projet : {_sanitize_html(project_name)}</h2>
        <p style="color: #555;">Votre vidéo <strong>{_sanitize_html(video_title)}</strong> a été générée avec succès.</p>
        <div style="text-align: center; margin: 30px 0;">
          <a href="{_sanitize_url(video_url)}"
             style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
            Voir la vidéo
          </a>
        </div>
        <p style="color: #999; font-size: 12px;">
          Cet email a été envoyé automatiquement par Reetik.
        </p>
      </div>
    </body>
    </html>"""

    return _send_email(user_email, subject, html_body)


async def send_generation_failed_email(
    user_email: str,
    video_title: str,
    project_name: str,
    error_message: str = "",
) -> bool:
    """Envoie un email si la génération échoue."""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return False

    subject = "⚠️ Reetik — Échec de génération vidéo"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #e74c3c; padding: 30px; text-align: center;">
        <h1 style="color: white; margin: 0;">⚠️ Reetik</h1>
      </div>
      <div style="padding: 30px; background: #f8f9fa;">
        <h2 style="color: #333;">Projet : {_sanitize_html(project_name)}</h2>
        <p style="color: #555;">La génération de <strong>{_sanitize_html(video_title)}</strong> a rencontré une erreur.</p>
        {"<p style='color: #999;'>Détail : " + _sanitize_html(error_message) + "</p>" if error_message else ""}
        <p style="color: #555;">Vous pouvez relancer la génération depuis l'application.</p>
      </div>
    </body>
    </html>"""

    return _send_email(user_email, subject, html_body)


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Envoie un email via SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.NOTIFICATION_FROM_EMAIL or settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_PORT != 25:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        logger.info(f"Email envoyé à {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Erreur envoi email à {to_email}: {e}")
        return False


def _sanitize_html(text: str) -> str:
    """Sanitize text for safe HTML insertion."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def _sanitize_url(url: str) -> str:
    """Sanitize URL to prevent XSS via javascript: or data: schemes."""
    if not url:
        return "#"
    url = url.strip()
    if url.lower().startswith(("javascript:", "data:", "vbscript:")):
        return "#"
    return _sanitize_html(url)
