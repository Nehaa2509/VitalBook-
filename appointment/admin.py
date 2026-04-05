from django.contrib import admin
from .models import Doctor, Patient, Appointment, Specialization, Review, ContactMessage, Billing, Prescription, Payment, OTPVerification


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
    list_display = [
        'id', 'patient_name', 'doctor_name', 
        'date', 'time', 'status_badge',
        'payment_status_display', 'action_buttons'
    ]
    list_filter = ['status', 'date', 'doctor__specialization']
    search_fields = ['patient__user__username', 'patient__name', 'doctor__name']
    date_hierarchy = 'date'
    ordering = ['-date', '-time']
    list_per_page = 20
    
    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        return f'Dr. {obj.doctor.name}'
    doctor_name.short_description = 'Doctor'
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        colors = {
            'Pending': '#ffc107',
            'Confirmed': '#28a745',
            'Completed': '#0d6efd',
            'Cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;'
            'border-radius:20px;font-size:12px;font-weight:600;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def payment_status_display(self, obj):
        from django.utils.html import format_html
        has_payment = obj.payments.filter(payment_status='Completed').exists()
        if has_payment:
            return format_html(
                '<span style="color:#28a745;font-weight:600;">✅ Paid</span>'
            )
        return format_html(
            '<span style="color:#dc3545;font-weight:600;">❌ Unpaid</span>'
        )
    payment_status_display.short_description = 'Payment'
    
    def action_buttons(self, obj):
        from django.utils.html import format_html
        if obj.status == 'Pending':
            return format_html(
                '<a href="/admin/appointment/appointment/{}/change/" '
                'style="background:#28a745;color:white;padding:4px 10px;'
                'border-radius:6px;text-decoration:none;margin-right:4px;font-size:11px;">'
                '✅ Edit</a>'
            )
        return format_html(
            '<span style="color:#6c757d;font-size:11px;">{}</span>', obj.status
        )
    action_buttons.short_description = 'Actions'
    
    # Custom admin actions
    actions = ['confirm_appointments', 'cancel_appointments', 'mark_completed']
    
    @admin.action(description='✅ Confirm selected appointments')
    def confirm_appointments(self, request, queryset):
        # This updates all selected rows at once
        updated_count = queryset.update(status='Confirmed')
        self.message_user(request, f"{updated_count} appointments have been successfully confirmed.")
    
    @admin.action(description='❌ Cancel selected appointments')
    def cancel_appointments(self, request, queryset):
        updated = queryset.exclude(status='Cancelled').update(status='Cancelled')
        self.message_user(request, f'{updated} appointments cancelled.')
    
    @admin.action(description='✔️ Mark as completed')
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='Confirmed').update(status='Completed')
        self.message_user(request, f'{updated} appointments marked as completed.')
    
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



@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'otp_type', 'is_verified', 'is_expired_display', 'created_at', 'expires_at']
    list_filter = ['otp_type', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'otp']
    readonly_fields = ['created_at', 'expires_at']
    
    def is_expired_display(self, obj):
        from django.utils.html import format_html
        if obj.is_expired():
            return format_html('<span style="color:#dc3545;font-weight:600;">❌ Expired</span>')
        return format_html('<span style="color:#28a745;font-weight:600;">✅ Valid</span>')
    is_expired_display.short_description = 'Status'
