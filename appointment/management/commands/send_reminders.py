"""
Management command to send appointment reminders.
Run this daily (e.g., via cron job) to send 24-hour reminders.

Usage:
    python manage.py send_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointment.models import Appointment
from appointment import email_utils


class Command(BaseCommand):
    help = 'Send appointment reminders for appointments scheduled tomorrow'

    def handle(self, *args, **options):
        # Get tomorrow's date
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Find all confirmed appointments for tomorrow
        appointments = Appointment.objects.filter(
            date=tomorrow,
            status='Confirmed'
        ).select_related('patient', 'doctor')
        
        sent_count = 0
        failed_count = 0
        
        self.stdout.write(f'Found {appointments.count()} appointments for {tomorrow}')
        
        for appointment in appointments:
            try:
                success = email_utils.send_appointment_reminder(appointment)
                if success:
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Sent reminder to {appointment.patient.name} '
                            f'for appointment with Dr. {appointment.doctor.name}'
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Failed to send reminder to {appointment.patient.name} '
                            f'(no email address)'
                        )
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error sending reminder to {appointment.patient.name}: {str(e)}'
                    )
                )
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  Total appointments: {appointments.count()}')
        self.stdout.write(self.style.SUCCESS(f'  Successfully sent: {sent_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.WARNING(f'  Failed: {failed_count}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Reminder job completed'))
