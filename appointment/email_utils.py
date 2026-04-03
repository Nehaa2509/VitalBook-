"""
Email utility functions for VitalBook.
Sends professional HTML emails for all key events.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_appointment_confirmation(appointment):
    """Send booking confirmation email to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'✅ Appointment Confirmed – VitalBook (#{appointment.id})'
        context = {
            'appointment': appointment,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
        }
        
        html_content = render_to_string('emails/appointment_confirmation.html', context)
        text_content = f'Your appointment with Dr. {appointment.doctor.name} is confirmed for {appointment.date} at {appointment.time}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False


def send_appointment_cancelled(appointment, cancelled_by='patient'):
    """Send cancellation email to both patient and doctor."""
    try:
        # Email to patient
        if appointment.patient.user and appointment.patient.user.email:
            subject = f'❌ Appointment Cancelled – VitalBook (#{appointment.id})'
            context = {
                'appointment': appointment,
                'cancelled_by': cancelled_by,
            }
            
            html_content = render_to_string('emails/appointment_cancelled.html', context)
            text_content = f'Your appointment with Dr. {appointment.doctor.name} on {appointment.date} has been cancelled.'
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.patient.user.email]
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=True)
        
        # Email to doctor (if doctor has user account)
        if appointment.doctor.user and appointment.doctor.user.email:
            subject_doctor = f'📋 Appointment Cancelled by Patient – VitalBook'
            html_doctor = render_to_string('emails/doctor_cancellation_notice.html', context)
            
            email2 = EmailMultiAlternatives(
                subject_doctor,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.doctor.user.email]
            )
            email2.attach_alternative(html_doctor, 'text/html')
            email2.send(fail_silently=True)
        
        return True
    except Exception as e:
        print(f"Error sending cancellation email: {e}")
        return False


def send_appointment_reminder(appointment):
    """Send 24-hour reminder to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'⏰ Reminder: Appointment Tomorrow – VitalBook'
        context = {'appointment': appointment}
        
        html_content = render_to_string('emails/appointment_reminder.html', context)
        text_content = f'Reminder: You have an appointment with Dr. {appointment.doctor.name} tomorrow at {appointment.time}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending reminder email: {e}")
        return False


def send_payment_receipt(appointment, payment):
    """Send payment receipt to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'💳 Payment Receipt – VitalBook (Booking #{appointment.id})'
        context = {
            'appointment': appointment,
            'payment': payment,
        }
        
        html_content = render_to_string('emails/payment_receipt.html', context)
        text_content = f'Payment of ₹{payment.amount} received for your appointment with Dr. {appointment.doctor.name}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending payment receipt email: {e}")
        return False


def send_review_thankyou(review):
    """Send thank you email after patient submits review."""
    try:
        if not review.patient.user or not review.patient.user.email:
            return False
        
        subject = '⭐ Thank You for Your Review – VitalBook'
        context = {'review': review}
        
        html_content = render_to_string('emails/review_thankyou.html', context)
        text_content = f'Thank you for reviewing Dr. {review.doctor.name} on VitalBook.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [review.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending review thank you email: {e}")
        return False


def send_welcome_email(user, patient):
    """Send welcome email to new patients."""
    try:
        if not user.email:
            return False
        
        subject = '👋 Welcome to VitalBook!'
        context = {
            'user': user,
            'patient': patient,
        }
        
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = f'Welcome to VitalBook, {patient.name}! Your account has been created successfully.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
