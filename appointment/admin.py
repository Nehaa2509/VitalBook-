from django.contrib import admin
from .models import Doctor, Patient, Appointment, Specialization, Review, ContactMessage, Billing, Prescription, Payment, Payment


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'experience_years', 'consultation_fee', 'rating', 'is_available', 'phone']
    list_filter = ['specialization', 'is_available', 'experience_years']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_available', 'rating']
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'image')
        }),
        ('Professional Details', {
            'fields': ('specialization', 'qualification', 'experience_years', 'bio', 'rating')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_time', 'is_available')
        }),
        ('Financial', {
            'fields': ('consultation_fee',)
        }),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'gender', 'blood_group', 'created_at']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['name', 'email', 'phone']
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'email', 'phone', 'date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Details', {
            'fields': ('address', 'emergency_contact')
        }),
        ('Medical Information', {
            'fields': ('medical_history',)
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time', 'status', 'cancellation_fee_applied', 'created_at']
    list_filter = ['status', 'date', 'doctor', 'created_at']
    search_fields = ['patient__name', 'doctor__name', 'reason']
    date_hierarchy = 'date'
    list_editable = ['status']
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'date', 'time', 'status')
        }),
        ('Patient Information', {
            'fields': ('reason', 'symptoms')
        }),
        ('Doctor Notes', {
            'fields': ('notes', 'prescription')
        }),
        ('Cancellation & QR', {
            'fields': ('cancellation_fee_applied', 'cancelled_at', 'qr_code'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'billing_type', 'total_amount', 'is_paid', 'created_at']
    list_filter = ['billing_type', 'is_paid', 'created_at']
    search_fields = ['appointment__patient__name', 'appointment__doctor__name']
    list_editable = ['is_paid']
    readonly_fields = ['created_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'issued_on']
    search_fields = ['appointment__patient__name', 'appointment__doctor__name', 'medicines']
    readonly_fields = ['issued_on']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'rating', 'created_at', 'appointment']
    list_filter = ['rating', 'created_at', 'doctor']
    search_fields = ['doctor__name', 'patient__name', 'comment']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Review Information', {
            'fields': ('doctor', 'patient', 'appointment', 'rating')
        }),
        ('Content', {
            'fields': ('comment',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'appointment', 'amount', 'payment_status', 'payment_method', 'payment_date', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'appointment__patient__name', 'appointment__doctor__name']
    list_editable = ['payment_status']
    readonly_fields = ['transaction_id', 'created_at', 'payment_date']
    fieldsets = (
        ('Payment Information', {
            'fields': ('appointment', 'amount', 'transaction_id')
        }),
        ('Status & Method', {
            'fields': ('payment_status', 'payment_method', 'payment_date')
        }),
    )
