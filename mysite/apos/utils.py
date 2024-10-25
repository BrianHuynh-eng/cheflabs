from twilio.rest import Client
from django.conf import settings
import random

def send_verification_code(phone_number):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    verification_code = random.randint(100000, 999999)

    message = client.messages.create(
        body=f'Your verification code is {verification_code}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    return verification_code
