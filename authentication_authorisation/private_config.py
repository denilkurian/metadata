


GOOGLE_CLIENT_ID = "776635407081-a1dhm9214g8cqatujv7rsbcbge5mff8b.apps.googleusercontent.com"

GOOGLE_CLIENT_SECRET = "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"


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  
SMTP_USERNAME = "denilk@datapmi.com"
SMTP_PASSWORD = "gjjtderpsuuxtvgp"
SENDER_EMAIL = "denilk@datapmi.com"
RECIPIENT_EMAIL = "denilkuriancc@gmail.com"

SECRET_KEY = "4315b1762ca7119834104e63d093c2d4"



ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES=30



import secrets

random_token = secrets.token_hex(16)
print("Random Token:", random_token)








