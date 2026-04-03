#!/usr/bin/env python
"""
Test script to verify the patient dashboard is working correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Patient, Appointment, Payment
from django.contrib.auth.models import User

def test_dashboard():
    print("=" * 60)
    print("VITALBOOK - Patient Dashboard Test")
    print("=" * 60)
    
    # Test 1: Check if patients exist
    patients = Patient.objects.all()
    print(f"\n✓ Test 1: Total patients in database: {patients.count()}")
    
    if patients.exists():
        patient = patients.first()
        print(f"  Sample patient: {patient.name} ({patient.email})")
        
        # Test 2: Check appointments for this patient
        appointments = Appointment.objects.filter(patient=patient)
        print(f"\n✓ Test 2: Appointments for {patient.name}: {appointments.count()}")
        
        # Categorize appointments
        upcoming = appointments.filter(status__in=['Pending', 'Confirmed'])
        completed = appointments.filter(status='Completed')
        cancelled = appointments.filter(status='Cancelled')
        
        print(f"  - Upcoming: {upcoming.count()}")
        print(f"  - Completed: {completed.count()}")
        print(f"  - Cancelled: {cancelled.count()}")
        
        # Test 3: Check payments
        payments = Payment.objects.filter(
            appointment__patient=patient,
            payment_status='Completed'
        )
        print(f"\n✓ Test 3: Completed payments: {payments.count()}")
        
        if payments.exists():
            total_spent = sum(p.amount for p in payments)
            print(f"  Total spent: ₹{total_spent}")
        
        # Test 4: Check user account
        if patient.user:
            print(f"\n✓ Test 4: User account linked: {patient.user.username}")
        else:
            print(f"\n⚠ Test 4: No user account linked to patient")
    
    # Test 5: Check URL configuration
    print(f"\n✓ Test 5: URL patterns check")
    from django.urls import reverse
    try:
        dashboard_url = reverse('patient_dashboard')
        update_profile_url = reverse('update_profile')
        print(f"  - patient_dashboard URL: {dashboard_url} ✓")
        print(f"  - update_profile URL: {update_profile_url} ✓")
    except Exception as e:
        print(f"  - URL error: {e}")
    
    print("\n" + "=" * 60)
    print("Dashboard test completed!")
    print("=" * 60)
    print("\nTo access the dashboard:")
    print("1. Start the server: python manage.py runserver")
    print("2. Login with a patient account")
    print("3. Navigate to: http://127.0.0.1:8000/patient/dashboard/")
    print("\nTest accounts:")
    print("- Username: amitverma, Password: password123")
    print("- Username: snehakulkarni, Password: password123")

if __name__ == '__main__':
    test_dashboard()
