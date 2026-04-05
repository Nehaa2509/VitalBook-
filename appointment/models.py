from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta



class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-stethoscope')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    available_days = models.CharField(max_length=100, help_text="e.g., Mon-Fri")
    available_time = models.CharField(max_length=100, help_text="e.g., 9:00 AM - 5:00 PM")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    bio = models.TextField(blank=True)
    image = models.CharField(max_length=200, blank=True, default='default-doctor.jpg')
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
    
    def get_appointment_count(self):
        return self.appointment_set.count()
    
    class Meta:
        ordering = ['-rating', 'name']


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Doctor's notes")
    prescription = models.TextField(blank=True)
    cancellation_fee_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name} - Dr. {self.doctor.name} on {self.date}"
    
    def is_upcoming(self):
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return appointment_datetime > timezone.now() and self.status in ['Pending', 'Confirmed']

    def can_cancel_free(self):
        """Returns True if the appointment was booked less than 24 hours ago (free cancellation window)."""
        if self.created_at:
            return timezone.now() - self.created_at < timedelta(hours=24)
        return False

    @property
    def has_completed_payment(self):
        """Returns True if this appointment has a completed payment."""
        return self.payments.filter(payment_status='Completed').exists()

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['doctor', 'date', 'time']


class Billing(models.Model):
    BILLING_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Cancellation Fee', 'Cancellation Fee'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='billings')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    billing_type = models.CharField(max_length=50, choices=BILLING_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.billing_type} - ₹{self.total_amount} for {self.appointment}"

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Card', 'Debit/Credit Card'),
        ('NetBanking', 'Net Banking'),
        ('Wallet', 'Wallet'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment #{self.transaction_id} - ₹{self.amount} ({self.payment_status})"
    
    class Meta:
        ordering = ['-created_at']


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription_record')
    medicines = models.TextField(help_text="Format: Medicine Name - Dosage - Duration")
    instructions = models.TextField(blank=True)
    issued_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient.name} by Dr. {self.appointment.doctor.name}"

    class Meta:
        ordering = ['-issued_on']


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reviews', null=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        patient_name = self.patient.name if self.patient else self.appointment.patient.name
        doctor_name = self.doctor.name if self.doctor else self.appointment.doctor.name
        return f"Review by {patient_name} for Dr. {doctor_name} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        # Auto-populate doctor and patient from appointment if not set
        if not self.doctor:
            self.doctor = self.appointment.doctor
        if not self.patient:
            self.patient = self.appointment.patient
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


import random

class OTPVerification(models.Model):
    OTP_TYPE_CHOICES = [
        ('email', 'Email'),
        ('mobile', 'Mobile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES, default='email')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.otp
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_type} - {'Verified' if self.is_verified else 'Pending'}"
    
    class Meta:
        ordering = ['-created_at']
