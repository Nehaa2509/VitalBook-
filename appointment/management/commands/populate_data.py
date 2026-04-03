from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointment.models import Specialization, Doctor, Patient, Appointment
from datetime import date, time, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        Doctor.objects.all().delete()
        Specialization.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating specializations...')
        specializations = {
            'Cardiology': Specialization.objects.create(
                name='Cardiology',
                description='Heart and cardiovascular system specialists',
                icon='fa-heart'
            ),
            'Neurology': Specialization.objects.create(
                name='Neurology',
                description='Brain and nervous system specialists',
                icon='fa-brain'
            ),
            'Orthopedics': Specialization.objects.create(
                name='Orthopedics',
                description='Bone and joint specialists',
                icon='fa-bone'
            ),
            'Pediatrics': Specialization.objects.create(
                name='Pediatrics',
                description='Child healthcare specialists',
                icon='fa-child'
            ),
            'Dermatology': Specialization.objects.create(
                name='Dermatology',
                description='Skin care specialists',
                icon='fa-hand-sparkles'
            ),
        }

        self.stdout.write('Creating doctors...')
        doctors_data = [
            {
                'name': 'Rajesh Sharma',
                'specialization': specializations['Cardiology'],
                'qualification': 'MD, DM (Cardiology)',
                'experience_years': 15,
                'available_days': 'Mon-Fri',
                'available_time': '9:00 AM - 5:00 PM',
                'consultation_fee': Decimal('800.00'),
                'email': 'rajesh.sharma@vitalbook.in',
                'phone': '+91 98765 43210',
                'bio': 'Experienced cardiologist specializing in heart disease prevention and treatment.',
                'rating': Decimal('4.8')
            },
            {
                'name': 'Ananya Iyer',
                'specialization': specializations['Neurology'],
                'qualification': 'MD, DM (Neurology)',
                'experience_years': 12,
                'available_days': 'Mon-Sat',
                'available_time': '10:00 AM - 6:00 PM',
                'consultation_fee': Decimal('1000.00'),
                'email': 'ananya.iyer@vitalbook.in',
                'phone': '+91 98765 43211',
                'bio': 'Neurologist with expertise in treating neurological disorders and brain health.',
                'rating': Decimal('4.9')
            },
            {
                'name': 'Vikram Malhotra',
                'specialization': specializations['Orthopedics'],
                'qualification': 'MS (Orthopaedics)',
                'experience_years': 10,
                'available_days': 'Tue-Sat',
                'available_time': '8:00 AM - 4:00 PM',
                'consultation_fee': Decimal('900.00'),
                'email': 'vikram.malhotra@vitalbook.in',
                'phone': '+91 98765 43212',
                'bio': 'Orthopedic surgeon specializing in joint replacement and sports injuries.',
                'rating': Decimal('4.7')
            },
            {
                'name': 'Priya Nair',
                'specialization': specializations['Pediatrics'],
                'qualification': 'MD (Pediatrics), DCH',
                'experience_years': 8,
                'available_days': 'Mon-Fri',
                'available_time': '9:00 AM - 5:00 PM',
                'consultation_fee': Decimal('600.00'),
                'email': 'priya.nair@vitalbook.in',
                'phone': '+91 98765 43213',
                'bio': 'Pediatrician dedicated to providing comprehensive care for children.',
                'rating': Decimal('4.9')
            },
            {
                'name': 'Suresh Patel',
                'specialization': specializations['Dermatology'],
                'qualification': 'MD (Dermatology), DVD',
                'experience_years': 14,
                'available_days': 'Mon-Thu',
                'available_time': '10:00 AM - 6:00 PM',
                'consultation_fee': Decimal('700.00'),
                'email': 'suresh.patel@vitalbook.in',
                'phone': '+91 98765 43214',
                'bio': 'Dermatologist specializing in medical and cosmetic dermatology.',
                'rating': Decimal('4.6')
            },
        ]

        doctors = []
        for doc_data in doctors_data:
            doctor = Doctor.objects.create(**doc_data)
            doctors.append(doctor)
            self.stdout.write(f'  Created: Dr. {doctor.name}')

        self.stdout.write('Creating users and patients...')
        users_data = [
            {
                'username': 'amit_verma',
                'email': 'amit.verma@gmail.com',
                'first_name': 'Amit',
                'last_name': 'Verma',
                'password': 'password123',
                'patient': {
                    'name': 'Amit Verma',
                    'email': 'amit.verma@gmail.com',
                    'phone': '+91 99887 76655',
                    'date_of_birth': date(1985, 5, 15),
                    'gender': 'Male',
                    'blood_group': 'O+',
                    'address': '12, Shivaji Nagar, Pune, Maharashtra 411005',
                    'emergency_contact': '+91 99887 76656',
                }
            },
            {
                'username': 'sneha_kulkarni',
                'email': 'sneha.kulkarni@gmail.com',
                'first_name': 'Sneha',
                'last_name': 'Kulkarni',
                'password': 'password123',
                'patient': {
                    'name': 'Sneha Kulkarni',
                    'email': 'sneha.kulkarni@gmail.com',
                    'phone': '+91 99887 77766',
                    'date_of_birth': date(1990, 8, 22),
                    'gender': 'Female',
                    'blood_group': 'A+',
                    'address': '45, MG Road, Bengaluru, Karnataka 560001',
                    'emergency_contact': '+91 99887 77767',
                }
            },
            {
                'username': 'rahul_gupta',
                'email': 'rahul.gupta@gmail.com',
                'first_name': 'Rahul',
                'last_name': 'Gupta',
                'password': 'password123',
                'patient': {
                    'name': 'Rahul Gupta',
                    'email': 'rahul.gupta@gmail.com',
                    'phone': '+91 99887 78877',
                    'date_of_birth': date(1978, 3, 10),
                    'gender': 'Male',
                    'blood_group': 'B+',
                    'address': '78, Connaught Place, New Delhi 110001',
                    'emergency_contact': '+91 99887 78878',
                }
            },
            {
                'username': 'divya_menon',
                'email': 'divya.menon@gmail.com',
                'first_name': 'Divya',
                'last_name': 'Menon',
                'password': 'password123',
                'patient': {
                    'name': 'Divya Menon',
                    'email': 'divya.menon@gmail.com',
                    'phone': '+91 99887 79988',
                    'date_of_birth': date(1992, 11, 5),
                    'gender': 'Female',
                    'blood_group': 'AB+',
                    'address': '23, Marine Drive, Mumbai, Maharashtra 400002',
                    'emergency_contact': '+91 99887 79989',
                }
            },
        ]

        patients = []
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password']
            )
            patient = Patient.objects.create(
                user=user,
                **user_data['patient']
            )
            patients.append(patient)
            self.stdout.write(f'  Created: {patient.name}')

        self.stdout.write('Creating appointments...')
        today = date.today()
        appointments_data = [
            {
                'patient': patients[0],
                'doctor': doctors[0],
                'date': today + timedelta(days=2),
                'time': time(10, 0),
                'status': 'Confirmed',
                'reason': 'Regular checkup',
                'symptoms': 'Chest pain, shortness of breath'
            },
            {
                'patient': patients[1],
                'doctor': doctors[3],
                'date': today + timedelta(days=1),
                'time': time(14, 0),
                'status': 'Pending',
                'reason': 'Child vaccination',
                'symptoms': 'Routine vaccination'
            },
            {
                'patient': patients[2],
                'doctor': doctors[2],
                'date': today + timedelta(days=5),
                'time': time(11, 30),
                'status': 'Confirmed',
                'reason': 'Knee pain',
                'symptoms': 'Pain in left knee, difficulty walking'
            },
            {
                'patient': patients[0],
                'doctor': doctors[1],
                'date': today - timedelta(days=10),
                'time': time(9, 0),
                'status': 'Completed',
                'reason': 'Headache consultation',
                'symptoms': 'Severe headaches',
                'notes': 'Prescribed medication, follow-up in 2 weeks'
            },
        ]

        for appt_data in appointments_data:
            appointment = Appointment.objects.create(**appt_data)
            self.stdout.write(f'  Created: {appointment}')

        self.stdout.write('Creating superuser...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@vitalbook.in',
                password='admin123'
            )
            self.stdout.write('  Created: admin (username: admin, password: admin123)')

        self.stdout.write(self.style.SUCCESS('\nDatabase populated successfully!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  Specializations: {Specialization.objects.count()}')
        self.stdout.write(f'  Doctors: {Doctor.objects.count()}')
        self.stdout.write(f'  Patients: {Patient.objects.count()}')
        self.stdout.write(f'  Appointments: {Appointment.objects.count()}')
        self.stdout.write('\nAdmin credentials:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('\nPatient login credentials (all use password: password123):')
        self.stdout.write('  - amit_verma')
        self.stdout.write('  - sneha_kulkarni')
        self.stdout.write('  - rahul_gupta')
        self.stdout.write('  - divya_menon')
