import logging

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


class TransactionalEmailError(Exception):
    """Raised when the configured transactional email provider rejects a send."""


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
    if _zeptomail_authorization_header():
        return _send_with_zeptomail(
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
    return _send_with_django_email(
        to_email,
        subject,
        html_body,
        text_body,
        from_email=from_email,
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


def _send_with_django_email(to_email, subject, html_body, text_body="", from_email=None):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body or "Please view this email in an HTML-capable email client.",
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body, "text/html")
    sent_count = message.send(fail_silently=False)
    logger.info("Sent transactional email with Django backend to %s", to_email)
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
