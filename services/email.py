from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from services.auth import auth_service
import os

print(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))

conf = ConnectionConfig(
    MAIL_USERNAME="2fcde6d3b52f1a",  # Логин из Mailtrap
    MAIL_PASSWORD="a07f7463f1dffc",  # Пароль из Mailtrap
    MAIL_FROM="noreply@example.com",
    MAIL_PORT=2525,  # Порт для TLS
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_FROM_NAME="Test App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,  # Отключите SSL, если используете TLS
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

async def send_reset_email(email: EmailStr, token: str, host: str):
    try:
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={"host": host, "token": token, "username": email.split("@")[0]},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset_email.html")
    except ConnectionErrors as err:
        print(err)
