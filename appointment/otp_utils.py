"""
OTP utility functions for VitalBook.
Handles email and SMS OTP sending.
"""
from django.core.mail import send_mail
from django.conf import settings


def send_email_otp(user, otp):
    """Send OTP via email."""
    try:
        subject = 'VitalBook – Your OTP Verification Code'
        message = f'''
Dear {user.get_full_name() or user.username},

Your OTP verification code is: {otp}

This code expires in 10 minutes.
Do not share this code with anyone.

Team VitalBook
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        return True
    except Exception as e:
        print(f"Error sending email OTP: {e}")
        return False


def send_mobile_otp(mobile_number, otp):
    """Send OTP via SMS using Twilio."""
    try:
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message = client.messages.create(
            body=f'Your VitalBook OTP is: {otp}. Valid for 10 minutes.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile_number
        )
        
        return True
    except Exception as e:
        print(f"Error sending mobile OTP: {e}")
        return False
