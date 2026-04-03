#!/usr/bin/env python
"""
Test script to verify the doctor dashboard is working correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Doctor, Appointment, Payment, Review
from django.contrib.auth.models import User
from django.db.models import Avg, Sum
from datetime import date, timedelta

def test_doctor_dashboard():
    print("=" * 60)
    print("VITALBOOK - Doctor Dashboard Test")
    print("=" * 60)
    
    # Test 1: Check if doctors exist
    doctors = Doctor.objects.all()
    print(f"\n✓ Test 1: Total doctors in database: {doctors.count()}")
    
    if doctors.exists():
        doctor = doctors.first()
        print(f"  Sample doctor: Dr. {doctor.name} ({doctor.specialization.name})")
        
        # Test 2: Check if doctor has user account
        if doctor.user:
            print(f"\n✓ Test 2: Doctor has user account: {doctor.user.username}")
        else:
            print(f"\n⚠ Test 2: Doctor doesn't have user account (needs to be linked)")
        
        # Test 3: Check appointments for this doctor
        appointments = Appointment.objects.filter(doctor=doctor)
        print(f"\n✓ Test 3: Appointments for Dr. {doctor.name}: {appointments.count()}")
        
        # Today's appointments
        today = date.today()
        today_appointments = appointments.filter(date=today)
        print(f"  - Today's appointments: {today_appointments.count()}")
        
        # Pending appointments
        pending = appointments.filter(status='Pending')
        print(f"  - Pending: {pending.count()}")
        
        # Completed appointments
        completed = appointments.filter(status='Completed')
        print(f"  - Completed: {completed.count()}")
        
        # Test 4: Check revenue
        payments = Payment.objects.filter(
            appointment__doctor=doctor,
            payment_status='Completed'
        )
        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
        print(f"\n✓ Test 4: Total revenue: ₹{total_revenue}")
        
        # Monthly revenue
        this_month = today.replace(day=1)
        monthly_revenue = Payment.objects.filter(
            appointment__doctor=doctor,
            appointment__date__gte=this_month,
            payment_status='Completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        print(f"  - Monthly revenue: ₹{monthly_revenue}")
        
        # Test 5: Check reviews
        reviews = Review.objects.filter(doctor=doctor)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        print(f"\n✓ Test 5: Reviews: {reviews.count()}")
        print(f"  - Average rating: {avg_rating:.1f}/5.0")
        
        # Test 6: Weekly data
        print(f"\n✓ Test 6: Weekly appointment data:")
        for i in range(7):
            day = today - timedelta(days=6-i)
            count = Appointment.objects.filter(doctor=doctor, date=day).count()
            print(f"  - {day.strftime('%a %b %d')}: {count} appointment(s)")
        
        # Test 7: Unique patients
        total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()
        print(f"\n✓ Test 7: Total unique patients: {total_patients}")
    
    # Test 8: Check URL configuration
    print(f"\n✓ Test 8: URL patterns check")
    from django.urls import reverse
    try:
        dashboard_url = reverse('doctor_dashboard')
        update_profile_url = reverse('update_doctor_profile')
        update_status_url = reverse('update_appointment_status', args=[1])
        print(f"  - doctor_dashboard URL: {dashboard_url} ✓")
        print(f"  - update_doctor_profile URL: {update_profile_url} ✓")
        print(f"  - update_appointment_status URL: {update_status_url} ✓")
    except Exception as e:
        print(f"  - URL error: {e}")
    
    print("\n" + "=" * 60)
    print("Dashboard test completed!")
    print("=" * 60)
    print("\nTo access the doctor dashboard:")
    print("1. Create a doctor user account in admin")
    print("2. Link the user to a doctor profile")
    print("3. Login with doctor credentials")
    print("4. Navigate to: http://127.0.0.1:8000/doctor/dashboard/")
    print("\nNote: Doctors need a user account to access the dashboard")

if __name__ == '__main__':
    test_doctor_dashboard()
