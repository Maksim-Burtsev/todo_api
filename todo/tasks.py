import os
from email.mime.text import MIMEText

import smtplib
from dotenv import load_dotenv

from celery import shared_task


load_dotenv()


@shared_task
def send_code_on_email(code: int, user_email: str) -> None:
    """
    Отправляет код подтверждения на почту
    """

    sender = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)

    message = MIMEText(f"{code}")
    message["Subject"] = "Reset password"

    server.sendmail(sender, user_email, message.as_string())
