import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("login", "password")
        smtp.send_message(msg)
