# https://myaccount.google.com/apppasswords go to this link and get your password
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "tushar@trainingbasket.co")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "zfuz wysw gcxy hdxr")


def send_welcome_email(receiver_email, name, account_no, pin):
    subject = "Welcome to NexVault — Your Account is Ready"

    body = f"""
Hello {name},

Your NexVault account has been created successfully.

━━━━━━━━━━━━━━━━━━━━━━━
  Account No : {account_no}
  PIN        : {pin}
━━━━━━━━━━━━━━━━━━━━━━━

Please keep your PIN confidential and do not share it with anyone.

You can now login at your NexVault portal.

Regards,
NexVault Banking
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # ✅ Using SSL on port 465 — works on Railway (port 587/STARTTLS is blocked)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"Welcome email sent to {receiver_email}")

    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        raise  # re-raise so the caller's try/except can log it


def send_forget_pin(name, account_no, pin, receiver_email):
    subject = "NexVault — Your PIN Has Been Reset"

    body = f"""
Hello {name},

Your NexVault PIN has been reset as requested.

━━━━━━━━━━━━━━━━━━━━━━━
  Account No : {account_no}
  New PIN    : {pin}
━━━━━━━━━━━━━━━━━━━━━━━

If you did not request this reset, please contact support immediately.

Regards,
NexVault Banking
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # ✅ Using SSL on port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"PIN reset email sent to {receiver_email}")

    except Exception as e:
        print(f"Failed to send PIN reset email: {e}")
        raise
