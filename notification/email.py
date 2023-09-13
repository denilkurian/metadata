import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from fastapi import HTTPException


def send_email_notification(db_name):
    # Email configuration
    
    SMTP_SERVER = config('SMTP_SERVER', default='')
    SMTP_PORT = config('SMTP_PORT', default=587, cast=int)
    SMTP_USERNAME = config('SMTP_USERNAME', default='')
    SMTP_PASSWORD = config('SMTP_PASSWORD', default='')
    SENDER_EMAIL = config('SENDER_EMAIL', default='')
    RECIPIENT_EMAIL = config('RECIPIENT_EMAIL', default='')


    subject = f"Metadata Crawl Job Finished for {db_name}"
    message = f"The metadata crawl job for {db_name} has finished.Database metadata details such as table names column datatype etc are defined"

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
    
