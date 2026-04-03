from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Specialization, Doctor, Patient, Appointment, Review, Payment


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'icon']


class DoctorSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    appointment_count = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialization', 'specialization_name',
            'qualification', 'experience_years', 'available_days',
            'available_time', 'consultation_fee', 'email', 'phone',
            'bio', 'image', 'is_available', 'rating', 'appointment_count',
            'created_at',
        ]
        read_only_fields = ['rating', 'created_at']

    def get_appointment_count(self, obj):
        return obj.get_appointment_count()


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'email', 'phone', 'date_of_birth',
            'gender', 'blood_group', 'address', 'emergency_contact',
            'medical_history', 'age', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_age(self, obj):
        return obj.get_age()


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(
        source='doctor.specialization.name', read_only=True
    )
    is_upcoming = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'doctor_specialization', 'date', 'time', 'status',
            'reason', 'symptoms', 'notes', 'prescription',
            'is_upcoming', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_upcoming(self, obj):
        return obj.is_upcoming()

    def validate(self, data):
        # Prevent double-booking
        doctor = data.get('doctor')
        date = data.get('date')
        time = data.get('time')
        instance_id = self.instance.id if self.instance else None

        qs = Appointment.objects.filter(
            doctor=doctor, date=date, time=time
        ).exclude(status='Cancelled')

        if instance_id:
            qs = qs.exclude(id=instance_id)

        if qs.exists():
            raise serializers.ValidationError(
                "This time slot is already booked for the selected doctor."
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='appointment.patient.name', read_only=True
    )
    doctor_name = serializers.CharField(
        source='appointment.doctor.name', read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'appointment', 'patient_name', 'doctor_name',
            'rating', 'comment', 'created_at',
        ]
        read_only_fields = ['created_at']



class PaymentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='appointment.patient.name', read_only=True)
    doctor_name = serializers.CharField(source='appointment.doctor.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'appointment', 'patient_name', 'doctor_name',
            'amount', 'payment_status', 'payment_status_display',
            'payment_method', 'payment_method_display',
            'transaction_id', 'payment_date', 'created_at',
        ]
        read_only_fields = ['transaction_id', 'payment_date', 'created_at']
