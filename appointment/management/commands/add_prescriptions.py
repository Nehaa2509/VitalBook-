from django.core.management.base import BaseCommand
from appointment.models import Appointment, Prescription

class Command(BaseCommand):
    help = 'Add sample prescriptions for all completed appointments'

    def handle(self, *args, **kwargs):
        prescriptions_data = [
            {
                'doctor_keyword': 'Rajesh Sharma',
                'medicines': '''Aspirin 75mg - 1 Tablet (Morning) - 30 Days
Rosuvastatin 10mg - 1 Tablet (Bedtime) - 30 Days
Nitroglycerin 2.6mg - 1 Tablet (Twice Daily) - 15 Days''',
                'instructions': 'Take medicines after meals. Low-sodium diet. 15 minutes walking daily. Avoid heavy exercise. Follow-up in 15 days.'
            },
            {
                'doctor_keyword': 'Ananya Iyer',
                'medicines': '''Levetiracetam 500mg - 1 Tablet (Morning & Night) - 30 Days
Clobazam 10mg - 1 Tablet (Bedtime) - 30 Days
Vitamin B12 500mcg - 1 Tablet (Morning) - 60 Days''',
                'instructions': 'Take medicines strictly on time. Avoid driving or operating heavy machinery. No alcohol. Sleep at least 8 hours. Follow-up in 30 days.'
            },
            {
                'doctor_keyword': 'Vikram Malhotra',
                'medicines': '''Pantoprazole 40mg - 1 Tablet (Empty Stomach Morning) - 30 Days
Domperidone 10mg - 1 Tablet (Before Meals) - 15 Days
Sucralfate 1g - 1 Tablet (Before Bedtime) - 30 Days''',
                'instructions': 'Avoid spicy and oily foods. Eat small frequent meals. No smoking or alcohol. Drink plenty of water. Follow-up in 30 days.'
            },
            {
                'doctor_keyword': 'Priya Nair',
                'medicines': '''Metformin 500mg - 1 Tablet (Morning & Evening with meals) - 30 Days
Glimepiride 1mg - 1 Tablet (Before Breakfast) - 30 Days
Vitamin D3 60000 IU - 1 Tablet (Weekly) - 8 Weeks''',
                'instructions': 'Monitor blood sugar daily. Follow strict diabetic diet. Avoid sweets and refined carbs. 30 minutes walk daily. Follow-up in 30 days.'
            },
            {
                'doctor_keyword': 'Suresh Patel',
                'medicines': '''Amoxicillin 500mg - 1 Capsule (Three times daily) - 7 Days
Cetirizine 10mg - 1 Tablet (Bedtime) - 10 Days
Paracetamol 650mg - 1 Tablet (If fever above 101F) - 5 Days''',
                'instructions': 'Complete the full antibiotic course. Drink warm fluids. Rest adequately. Avoid cold foods and drinks. Follow-up if symptoms persist after 7 days.'
            },
            {
                'doctor_keyword': 'Meera Krishnan',
                'medicines': '''Amlodipine 5mg - 1 Tablet (Morning) - 30 Days
Telmisartan 40mg - 1 Tablet (Morning) - 30 Days
Atorvastatin 20mg - 1 Tablet (Bedtime) - 30 Days''',
                'instructions': 'Monitor BP daily at home. Low salt diet strictly. No smoking. Light exercise only. Avoid stress. Follow-up in 15 days.'
            },
            {
                'doctor_keyword': 'Arjun Kapoor',
                'medicines': '''Diclofenac 50mg - 1 Tablet (Twice daily after meals) - 10 Days
Thiocolchicoside 4mg - 1 Tablet (Morning & Night) - 7 Days
Calcium + Vitamin D3 - 1 Tablet (After Lunch) - 60 Days''',
                'instructions': 'Apply hot fomentation on affected area twice daily. Avoid lifting heavy objects. Do prescribed physiotherapy exercises. Follow-up in 2 weeks.'
            },
            {
                'doctor_keyword': 'Deepa Menon',
                'medicines': '''Levothyroxine 50mcg - 1 Tablet (Empty stomach morning) - 30 Days
Iron + Folic Acid - 1 Tablet (After Breakfast) - 30 Days
Calcium Carbonate 500mg - 1 Tablet (After Dinner) - 30 Days''',
                'instructions': 'Take thyroid medicine 30 minutes before breakfast. Get thyroid function test after 6 weeks. Avoid soy products near medicine time. Follow-up in 45 days.'
            },
        ]

        created_count = 0
        skipped_count = 0

        for data in prescriptions_data:
            # Find appointments for this doctor
            appointments = Appointment.objects.filter(
                doctor__name__icontains=data['doctor_keyword']
            )

            for appointment in appointments:
                # Check if prescription already exists
                if not hasattr(appointment, 'prescription'):
                    Prescription.objects.create(
                        appointment=appointment,
                        medicines=data['medicines'],
                        instructions=data['instructions']
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Prescription created for {appointment}'
                        )
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Prescription already exists for {appointment}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Done! Created: {created_count} | Skipped: {skipped_count}'
            )
        )
