import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "tushar@trainingbasket.co"  # https://myaccount.google.com/apppasswords go to this link and get your password
EMAIL_PASSWORD = "zfuz wysw gcxy hdxr"

def send_welcome_email(receiver_email, name, account_no, pin):

    subject = "Welcome to our Bank Service"

    body = f"""
    Hello {name},

    Thank you for registering with Apna Bank Bandhan.
    Login credentials: 
    Account No : {account_no}
    Pin : {pin} 

    You can now login.

    Regards,
    Tushar
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.send_message(msg)

    server.quit()

    print("Email sent successfully")

def send_forget_pin(name, account_no ,pin, receiver_email):
    subject = "Welcome to our Bank Service"

    body = f"""
    Hello {name},

    Regenerated pin for your account
    Login credentials: 
    Account No : {account_no}
    Pin : {pin} 

    You can now login.

    Regards,
    Tushar
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.send_message(msg)

    server.quit()

    print("Email sent successfully")