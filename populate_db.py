import os
import django
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from appointment.models import Specialization, Doctor, Patient, Appointment, Billing, Prescription

def create_dummy_data():
    print("Creating admin user...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Admin user created: admin / admin")
    else:
        print("Admin user already exists.")

    print("Creating Specializations...")
    specs_data = [
        {'name': 'Cardiology', 'description': 'Heart and blood vessel diseases.', 'icon': 'fa-heartbeat'},
        {'name': 'Neurology', 'description': 'Disorders of the nervous system.', 'icon': 'fa-brain'},
        {'name': 'Pediatrics', 'description': 'Medical care of infants, children, and adolescents.', 'icon': 'fa-baby'},
        {'name': 'Orthopedics', 'description': 'Conditions involving the musculoskeletal system.', 'icon': 'fa-bone'},
        {'name': 'General Medicine', 'description': 'Primary care and general health issues.', 'icon': 'fa-stethoscope'},
    ]
    
    specs = {}
    for data in specs_data:
        spec, created = Specialization.objects.get_or_create(name=data['name'], defaults={
            'description': data['description'],
            'icon': data['icon']
        })
        specs[data['name']] = spec
        if created:
            print(f"Created specialization: {spec.name}")

    print("Creating Doctors...")
    doctors_data = [
        {'name': 'Rahul Sharma', 'specialization': specs['Cardiology'], 'qualification': 'MD, DM Cardiology', 'experience': 15, 'fee': 1200, 'time': '10:00 AM - 02:00 PM', 'days': 'Mon-Sat'},
        {'name': 'Anita Desai', 'specialization': specs['Neurology'], 'qualification': 'MD, DM Neurology', 'experience': 12, 'fee': 1500, 'time': '11:00 AM - 05:00 PM', 'days': 'Mon-Fri'},
        {'name': 'Vikram Singh', 'specialization': specs['Pediatrics'], 'qualification': 'MD Pediatrics', 'experience': 8, 'fee': 800, 'time': '09:00 AM - 01:00 PM', 'days': 'Mon-Sat'},
        {'name': 'Priya Patel', 'specialization': specs['Orthopedics'], 'qualification': 'MS Orthopedics', 'experience': 20, 'fee': 1000, 'time': '04:00 PM - 08:00 PM', 'days': 'Mon-Wed, Fri'},
        {'name': 'Amit Kumar', 'specialization': specs['General Medicine'], 'qualification': 'MD Medicine', 'experience': 5, 'fee': 500, 'time': '09:00 AM - 06:00 PM', 'days': 'Mon-Sat'},
    ]

    for d in doctors_data:
        doc, created = Doctor.objects.get_or_create(name=d['name'], defaults={
            'specialization': d['specialization'],
            'qualification': d['qualification'],
            'experience_years': d['experience'],
            'consultation_fee': d['fee'],
            'available_time': d['time'],
            'available_days': d['days'],
            'phone': '+91 9876543210',
            'email': f"{d['name'].lower().replace(' ', '.')}@vitalbook.in",
            'rating': 4.5 + (0.1 * d['experience'] % 0.5)
        })
        if created:
            print(f"Created doctor: Dr. {doc.name}")

    print("Creating sample patient...")
    user, _ = User.objects.get_or_create(username='patient1', defaults={'email': 'patient1@example.com'})
    if _:
        user.set_password('patient123')
        user.save()
        
    patient, created = Patient.objects.get_or_create(user=user, defaults={
        'name': 'Ramesh Verma',
        'email': 'patient1@example.com',
        'phone': '+91 8888888888',
        'date_of_birth': date(1985, 5, 20),
        'gender': 'Male',
        'blood_group': 'O+'
    })
    
    if created:
        print(f"Created patient: {patient.name}")

    print("Data population complete!")

if __name__ == '__main__':
    create_dummy_data()
