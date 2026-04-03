"""
Test script for VitalBook email notification system.
Run with: python manage.py shell < test_email_system.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Appointment, Patient, Review, Payment
from appointment import email_utils
from django.contrib.auth.models import User

print("=" * 60)
print("VitalBook Email System Test")
print("=" * 60)
print()

# Test 1: Welcome Email
print("Test 1: Welcome Email")
print("-" * 60)
try:
    user = User.objects.filter(patient__isnull=False).first()
    if user and hasattr(user, 'patient'):
        patient = user.patient
        result = email_utils.send_welcome_email(user, patient)
        print(f"✓ Welcome email sent to {patient.name} ({user.email})")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No patient found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 2: Appointment Confirmation
print("Test 2: Appointment Confirmation")
print("-" * 60)
try:
    appointment = Appointment.objects.filter(
        patient__user__isnull=False,
        status='Confirmed'
    ).first()
    if appointment:
        result = email_utils.send_appointment_confirmation(appointment)
        print(f"✓ Confirmation email sent for appointment #{appointment.id}")
        print(f"  Patient: {appointment.patient.name}")
        print(f"  Doctor: Dr. {appointment.doctor.name}")
        print(f"  Date: {appointment.date}")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No confirmed appointment found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 3: Payment Receipt
print("Test 3: Payment Receipt")
print("-" * 60)
try:
    payment = Payment.objects.filter(
        appointment__patient__user__isnull=False,
        payment_status='Completed'
    ).first()
    if payment:
        result = email_utils.send_payment_receipt(payment.appointment, payment)
        print(f"✓ Receipt email sent for payment {payment.transaction_id}")
        print(f"  Amount: ₹{payment.amount}")
        print(f"  Patient: {payment.appointment.patient.name}")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No completed payment found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 4: Appointment Reminder
print("Test 4: Appointment Reminder")
print("-" * 60)
try:
    appointment = Appointment.objects.filter(
        patient__user__isnull=False,
        status='Confirmed'
    ).first()
    if appointment:
        result = email_utils.send_appointment_reminder(appointment)
        print(f"✓ Reminder email sent for appointment #{appointment.id}")
        print(f"  Patient: {appointment.patient.name}")
        print(f"  Doctor: Dr. {appointment.doctor.name}")
        print(f"  Date: {appointment.date}")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No confirmed appointment found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 5: Appointment Cancellation
print("Test 5: Appointment Cancellation")
print("-" * 60)
try:
    appointment = Appointment.objects.filter(
        patient__user__isnull=False,
        status='Cancelled'
    ).first()
    if appointment:
        result = email_utils.send_appointment_cancelled(appointment, cancelled_by='patient')
        print(f"✓ Cancellation email sent for appointment #{appointment.id}")
        print(f"  Patient: {appointment.patient.name}")
        print(f"  Doctor: Dr. {appointment.doctor.name}")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No cancelled appointment found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 6: Review Thank You
print("Test 6: Review Thank You")
print("-" * 60)
try:
    review = Review.objects.filter(
        patient__user__isnull=False
    ).first()
    if review:
        result = email_utils.send_review_thankyou(review)
        print(f"✓ Thank you email sent for review")
        print(f"  Patient: {review.patient.name}")
        print(f"  Doctor: Dr. {review.doctor.name}")
        print(f"  Rating: {review.rating}/5")
        print(f"  Result: {'Success' if result else 'Failed (no email)'}")
    else:
        print("✗ No review found for testing")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Summary
print("=" * 60)
print("Test Summary")
print("=" * 60)
print("All email functions have been tested.")
print("Check your console output to see the email content.")
print()
print("Note: Emails are sent to console in development mode.")
print("To send real emails, configure SMTP in settings.py")
print("=" * 60)
