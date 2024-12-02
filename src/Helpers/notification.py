# src/Helpers/notification.py

import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os
import logging
import warnings
from cryptography.utils import CryptographyDeprecationWarning

# Suppress specific cryptography deprecation warnings
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Configure logging
logging.basicConfig(
    filename='notification.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_email(subject, body, recipients):
    """
    Sends an email using Gmail's SMTP_SSL server.

    Args:
        subject (str): Subject of the email.
        body (str): Body of the email.
        recipients (list): List of recipient email addresses.

    Raises:
        ValueError: If sender email or password is not set in environment variables.
        Exception: If sending the email fails.
    """
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # SMTP_SSL port
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")

    if not sender or not password:
        logging.error("Sender email or password not set in environment variables.")
        raise ValueError("Sender email or password not set in environment variables.")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        logging.info(f"Email sent to {recipients} with subject '{subject}'.")
    except Exception as e:
        logging.error(f"Failed to send email to {recipients}: {e}")
        raise e

def send_sms_alert(message, recipient_phone):
    """
    Sends an SMS alert using Twilio's API.

    Args:
        message (str): The message content.
        recipient_phone (str): The recipient's phone number in E.164 format.

    Raises:
        ValueError: If Twilio credentials or phone number are not set in environment variables.
        Exception: If sending the SMS fails.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_phone:
        logging.error("Twilio credentials or phone number not set in environment variables.")
        raise ValueError("Twilio credentials or phone number not set in environment variables.")

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=from_phone,
            to=recipient_phone
        )
        print(f"SMS sent to {recipient_phone}.")
    except Exception as e:
        print(f"Failed to send SMS to {recipient_phone}: {e}")
        raise e
