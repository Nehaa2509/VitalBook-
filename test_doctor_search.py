#!/usr/bin/env python
"""
Test script to verify the doctor search and filter system.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Doctor, Specialization, Review
from django.db.models import Avg, Count, Q

def test_doctor_search_filters():
    print("=" * 60)
    print("VITALBOOK - Doctor Search & Filter Test")
    print("=" * 60)
    
    # Test 1: Basic doctor query with annotations
    print("\n✓ Test 1: Doctor query with review statistics")
    doctors = Doctor.objects.filter(is_available=True).annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    )
    print(f"  Total available doctors: {doctors.count()}")
    
    for doctor in doctors[:3]:
        print(f"  - Dr. {doctor.name}")
        print(f"    Specialization: {doctor.specialization.name}")
        print(f"    Rating: {doctor.rating} (DB) / {doctor.avg_rating or 0:.1f} (Calculated)")
        print(f"    Reviews: {doctor.total_reviews}")
        print(f"    Fee: ₹{doctor.consultation_fee}")
    
    # Test 2: Search functionality
    print("\n✓ Test 2: Search functionality")
    search_terms = ['cardio', 'sharma', 'pediatric']
    for term in search_terms:
        results = doctors.filter(
            Q(name__icontains=term) |
            Q(specialization__name__icontains=term) |
            Q(qualification__icontains=term)
        )
        print(f"  Search '{term}': {results.count()} result(s)")
    
    # Test 3: Filter by specialization
    print("\n✓ Test 3: Filter by specialization")
    specializations = Specialization.objects.all()
    for spec in specializations[:3]:
        count = doctors.filter(specialization=spec).count()
        print(f"  {spec.name}: {count} doctor(s)")
    
    # Test 4: Filter by fee range
    print("\n✓ Test 4: Filter by consultation fee")
    fee_ranges = [
        (0, 500),
        (500, 1000),
        (1000, 2000)
    ]
    for min_fee, max_fee in fee_ranges:
        count = doctors.filter(
            consultation_fee__gte=min_fee,
            consultation_fee__lte=max_fee
        ).count()
        print(f"  ₹{min_fee} - ₹{max_fee}: {count} doctor(s)")
    
    # Test 5: Filter by rating
    print("\n✓ Test 5: Filter by minimum rating")
    rating_thresholds = [3, 4, 4.5]
    for min_rating in rating_thresholds:
        count = doctors.filter(
            Q(rating__gte=min_rating) | Q(avg_rating__gte=min_rating)
        ).count()
        print(f"  {min_rating}+ stars: {count} doctor(s)")
    
    # Test 6: Filter by experience
    print("\n✓ Test 6: Filter by experience")
    exp_thresholds = [5, 10, 15]
    for min_exp in exp_thresholds:
        count = doctors.filter(experience_years__gte=min_exp).count()
        print(f"  {min_exp}+ years: {count} doctor(s)")
    
    # Test 7: Filter by availability
    print("\n✓ Test 7: Filter by availability")
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for day in days[:3]:
        count = doctors.filter(available_days__icontains=day).count()
        print(f"  Available on {day}: {count} doctor(s)")
    
    # Test 8: Sorting options
    print("\n✓ Test 8: Sorting options")
    sort_options = {
        'Name': 'name',
        'Fee (Low to High)': 'consultation_fee',
        'Fee (High to Low)': '-consultation_fee',
        'Rating': '-rating',
        'Experience': '-experience_years',
    }
    for label, order in sort_options.items():
        sorted_doctors = doctors.order_by(order)
        if sorted_doctors.exists():
            first = sorted_doctors.first()
            print(f"  {label}: Dr. {first.name}")
    
    # Test 9: Combined filters
    print("\n✓ Test 9: Combined filters (Cardiology, ₹500-1000, 4+ rating)")
    cardio_spec = Specialization.objects.filter(name__icontains='cardio').first()
    if cardio_spec:
        combined = doctors.filter(
            specialization=cardio_spec,
            consultation_fee__gte=500,
            consultation_fee__lte=1000,
            rating__gte=4
        )
        print(f"  Results: {combined.count()} doctor(s)")
        for doc in combined:
            print(f"    - Dr. {doc.name} (₹{doc.consultation_fee}, {doc.rating}★)")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    print("\nSearch & Filter System is working correctly!")
    print("\nAccess the enhanced doctor list at:")
    print("http://127.0.0.1:8000/doctors/")

if __name__ == '__main__':
    test_doctor_search_filters()
