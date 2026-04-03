#!/usr/bin/env python
"""
Test script to verify the has_completed_payment property works correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Appointment, Payment

def test_has_completed_payment():
    print("=" * 60)
    print("Testing has_completed_payment Property")
    print("=" * 60)
    
    # Get all appointments
    appointments = Appointment.objects.all()
    print(f"\nTotal appointments: {appointments.count()}")
    
    # Test the property
    for appointment in appointments[:5]:
        has_payment = appointment.has_completed_payment
        payment_count = appointment.payments.filter(payment_status='Completed').count()
        
        print(f"\nAppointment #{appointment.id}:")
        print(f"  Patient: {appointment.patient.name}")
        print(f"  Doctor: Dr. {appointment.doctor.name}")
        print(f"  Status: {appointment.status}")
        print(f"  has_completed_payment: {has_payment}")
        print(f"  Completed payments: {payment_count}")
        
        # Verify the property works correctly
        if payment_count > 0:
            assert has_payment == True, "Property should return True when payments exist"
            print("  ✓ Property working correctly (has payment)")
        else:
            assert has_payment == False, "Property should return False when no payments"
            print("  ✓ Property working correctly (no payment)")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nThe has_completed_payment property is working correctly.")
    print("Templates can now use: {% if appointment.has_completed_payment %}")

if __name__ == '__main__':
    test_has_completed_payment()
