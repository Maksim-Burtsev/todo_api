import os
from email.mime.text import MIMEText

import smtplib
from dotenv import load_dotenv

from celery import shared_task


load_dotenv()
SENDER = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


@shared_task
def send_code_on_email(code: int, user_email: str) -> None:
    """
    Отправляет код подтверждения на почту
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER, PASSWORD)

    message = MIMEText(f"{code}")
    message["Subject"] = "Reset PASSWORD"

    server.sendmail(SENDER, user_email, message.as_string())
