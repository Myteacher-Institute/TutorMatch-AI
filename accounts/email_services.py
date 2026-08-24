import logging
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection

logger = logging.getLogger(__name__)


class TransactionalEmailError(Exception):
    """Raised when all configured transactional email providers fail."""


def send_transactional_email(
    to_email,
    to_name,
    subject,
    html_body,
    text_body="",
    from_email=None,
    from_name=None,
    reply_to_email=None,
    reply_to_name=None,
):
    """
    Sends transactional email using a multi-provider automatic failover pipeline:
    1. ZeptoMail API (if credentials configured)
    2. Resend API (if RESEND_API_KEY configured)
    3. Brevo API (if BREVO_API_KEY / SENDINBLUE_API_KEY configured)
    4. Django Default Email Backend (SMTP / Gmail / Brevo SMTP)
    5. Console Emergency Fallback (if EMAIL_FAILOVER_TO_CONSOLE is True)
    """
    providers = []

    # 1. ZeptoMail API
    if _zeptomail_authorization_header():
        providers.append((
            "ZeptoMail API",
            lambda: _send_with_zeptomail(
                to_email,
                to_name,
                subject,
                html_body,
                text_body,
                from_email=from_email,
                from_name=from_name,
                reply_to_email=reply_to_email,
                reply_to_name=reply_to_name,
            )
        ))

    # 2. Resend API
    if getattr(settings, "RESEND_API_KEY", "").strip():
        providers.append((
            "Resend API",
            lambda: _send_with_resend(
                to_email,
                to_name,
                subject,
                html_body,
                text_body,
                from_email=from_email,
            )
        ))

    # 3. Brevo API (Sendinblue)
    if getattr(settings, "BREVO_API_KEY", "").strip():
        providers.append((
            "Brevo API",
            lambda: _send_with_brevo(
                to_email,
                to_name,
                subject,
                html_body,
                text_body,
                from_email=from_email,
                from_name=from_name,
            )
        ))

    # 4. Django Default Mail Backend (SMTP / Gmail / Brevo SMTP)
    providers.append((
        "Django SMTP / Mail Backend",
        lambda: _send_with_django_email(
            to_email,
            subject,
            html_body,
            text_body,
            from_email=from_email,
        )
    ))

    # 5. Console Emergency Fallback
    if getattr(settings, "EMAIL_FAILOVER_TO_CONSOLE", True):
        providers.append((
            "Console Emergency Fallback",
            lambda: _send_with_console_fallback(
                to_email,
                subject,
                html_body,
                text_body,
                from_email=from_email,
            )
        ))

    attempted = []
    last_error = None

    for provider_name, provider_func in providers:
        try:
            attempted.append(provider_name)
            result = provider_func()
            if len(attempted) > 1:
                logger.info(
                    "Successfully sent transactional email to %s using fallback provider '%s' after earlier failure(s) in %s",
                    to_email,
                    provider_name,
                    attempted[:-1],
                )
            return result
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Email provider '%s' failed to send email to %s: %s. Trying next provider in failover chain...",
                provider_name,
                to_email,
                exc,
            )

    raise TransactionalEmailError(
        f"All email providers ({', '.join(attempted)}) failed to send email to {to_email}. Last error: {last_error}"
    )


def _send_with_zeptomail(
    to_email,
    to_name,
    subject,
    html_body,
    text_body="",
    from_email=None,
    from_name=None,
    reply_to_email=None,
    reply_to_name=None,
):
    payload = {
        "from": {
            "address": from_email or settings.ZEPTOMAIL_FROM_EMAIL,
            "name": from_name or settings.ZEPTOMAIL_FROM_NAME,
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                    "name": to_name or to_email,
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body,
    }
    if text_body:
        payload["textbody"] = text_body
    reply_address = reply_to_email or settings.ZEPTOMAIL_REPLY_TO_EMAIL
    if reply_address:
        payload["reply_to"] = [
            {
                "address": reply_address,
                "name": reply_to_name or settings.ZEPTOMAIL_REPLY_TO_NAME,
            }
        ]

    response = requests.post(
        settings.ZEPTOMAIL_API_URL,
        json=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": _zeptomail_authorization_header(),
        },
        timeout=settings.ZEPTOMAIL_TIMEOUT_SECONDS,
    )
    if response.status_code >= 400:
        response_body = response.text.strip()[:600]
        logger.error(
            "ZeptoMail rejected transactional email to %s with status %s: %s",
            to_email,
            response.status_code,
            response_body,
        )
        raise TransactionalEmailError(
            f"ZeptoMail rejected email with status {response.status_code}: {response_body}"
        )
    logger.info("Sent transactional email with ZeptoMail to %s", to_email)
    return response


def _send_with_resend(to_email, to_name, subject, html_body, text_body="", from_email=None):
    resend_api_key = getattr(settings, "RESEND_API_KEY", "").strip()
    if not resend_api_key:
        raise TransactionalEmailError("Resend API key is not configured.")

    sender_email = from_email or getattr(settings, "RESEND_FROM_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
    payload = {
        "from": sender_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        payload["text"] = text_body

    response = requests.post(
        "https://api.resend.com/emails",
        json=payload,
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    if response.status_code >= 400:
        response_body = response.text.strip()[:600]
        logger.error("Resend rejected transactional email to %s with status %s: %s", to_email, response.status_code, response_body)
        raise TransactionalEmailError(f"Resend rejected email with status {response.status_code}: {response_body}")
    logger.info("Sent transactional email via Resend to %s", to_email)
    return response


def _send_with_brevo(to_email, to_name, subject, html_body, text_body="", from_email=None, from_name=None):
    brevo_api_key = getattr(settings, "BREVO_API_KEY", "").strip()
    if not brevo_api_key:
        raise TransactionalEmailError("Brevo API key is not configured.")

    sender_email = from_email or getattr(settings, "BREVO_FROM_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
    payload = {
        "sender": {"email": sender_email, "name": from_name or "MyteacherConnect"},
        "to": [{"email": to_email, "name": to_name or to_email}],
        "subject": subject,
        "htmlContent": html_body,
    }
    if text_body:
        payload["textContent"] = text_body

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers={
            "api-key": brevo_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=15,
    )
    if response.status_code >= 400:
        response_body = response.text.strip()[:600]
        logger.error("Brevo rejected transactional email to %s with status %s: %s", to_email, response.status_code, response_body)
        raise TransactionalEmailError(f"Brevo rejected email with status {response.status_code}: {response_body}")
    logger.info("Sent transactional email via Brevo to %s", to_email)
    return response


def _send_with_django_email(to_email, subject, html_body, text_body="", from_email=None):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body or "Please view this email in an HTML-capable email client.",
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body, "text/html")
    sent_count = message.send(fail_silently=False)
    if sent_count == 0:
        raise TransactionalEmailError("Django EmailBackend returned 0 emails sent.")
    logger.info("Sent transactional email with Django backend to %s", to_email)
    return sent_count


def _send_with_console_fallback(to_email, subject, html_body, text_body="", from_email=None):
    connection = get_connection("django.core.mail.backends.console.EmailBackend")
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body or html_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        connection=connection,
    )
    message.attach_alternative(html_body, "text/html")
    sent_count = message.send(fail_silently=False)
    logger.info("Logged transactional email via Console Emergency Fallback to %s", to_email)
    return sent_count


def _zeptomail_authorization_header():
    api_key = _clean_token(settings.ZEPTOMAIL_API_KEY)
    if api_key:
        if api_key.lower().startswith("zoho-enczapikey "):
            return f"Zoho-enczapikey {api_key.split(None, 1)[1].strip()}"
        return f"Zoho-enczapikey {api_key}"

    token = _clean_token(settings.ZEPTOMAIL_SEND_MAIL_TOKEN)
    if token:
        return f"Zoho-enczapikey {token}"

    return ""


def _clean_token(value):
    return (value or "").strip().strip('"').strip("'")
