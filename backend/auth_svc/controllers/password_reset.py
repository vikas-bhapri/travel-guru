import os, aiosmtplib, ssl
from email.message import EmailMessage
from fastapi import HTTPException, status
from ..schemas.auth_schema import EmailRequest
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_ADDR = os.getenv("FROM_ADDR", SMTP_USER)


async def send_email(email_request: EmailRequest):
    message = EmailMessage()
    message["from"] = FROM_ADDR
    message["to"] = email_request.to
    message["subject"] = email_request.subject
    if email_request.body_html:
        message.add_alternative(email_request.body_html, subtype="html")
    elif email_request.body_text:
        message.set_content(email_request.body_text)
    else:
        raise ValueError("Email must have either body_text or body_html")

    context = ssl.create_default_context()

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=SMTP_PORT == 587,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            tls_context=context,
            timeout=20,
        )

        return {"message": "Email sent successfully"}
    except aiosmtplib.SMTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
