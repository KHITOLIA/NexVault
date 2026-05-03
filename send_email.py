# https://myaccount.google.com/apppasswords go to this link and get your password
import os
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)


def send_welcome_email(receiver_email, name, account_no, pin):
    msg = Message(
        subject="Welcome to NexVault — Your Account is Ready",
        recipients=[receiver_email],
        body=f"""
Hello {name},

Your NexVault account has been created successfully.

━━━━━━━━━━━━━━━━━━━━━━━
  Account No : {account_no}
  PIN        : {pin}
━━━━━━━━━━━━━━━━━━━━━━━

Please keep your PIN confidential and do not share it with anyone.

Regards,
NexVault Banking
        """
    )
    mail.send(msg)
    print(f"Welcome email sent to {receiver_email}")


def send_forget_pin(name, account_no, pin, receiver_email):
    msg = Message(
        subject="NexVault — Your PIN Has Been Reset",
        recipients=[receiver_email],
        body=f"""
Hello {name},

Your NexVault PIN has been reset successfully.

━━━━━━━━━━━━━━━━━━━━━━━
  Account No : {account_no}
  New PIN    : {pin}
━━━━━━━━━━━━━━━━━━━━━━━

If you did not request this, contact support immediately.

Regards,
NexVault Banking
        """
    )
    mail.send(msg)
    print(f"PIN reset email sent to {receiver_email}")
