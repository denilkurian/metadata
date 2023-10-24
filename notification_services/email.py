
######### in this session when we fetch metadata details from any database and an email notification send to the configured mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from authentication_authorisation.private_config import *
from fastapi import HTTPException


def send_email_notification(db_name):

    subject = f"Metadata Crawl Job Finished for {db_name}"
    message = f"The metadata crawl job for {db_name} has been finished.Database metadata details such as table names column datatype etc are defined successfully"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")
    












