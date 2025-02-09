""" 
This module provides functionality for sending emails using FastAPI-Mail.

Classes:
Functions:
    send_email(email: EmailStr, username: str, host: str):
Exceptions:
Misc variables:
    conf: ConnectionConfig
        Configuration object for FastAPI-Mail. 
"""

from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.services.auth import create_email_token

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str, type: str = "verify"):
    """
    Sends an email to the user based on the specified type.

    Args:
        email (EmailStr): The email address of the user.
        username (str): The username of the user.
        host (str): The host of the server (used for the verification link).


    Returns:
        None
    """
    settings = {
        "verify": {
            "subject": "Confirm your email",
            "template": "verify_email.html",
        },
        "reset": {
            "subject": "Reset your password",
            "template": "reset_password.html",
        },
    }
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject=settings[type]["subject"],
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=settings[type]["template"])
    except ConnectionErrors as err:
        print(err)
