from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from .models import Specialization, Doctor, Patient, Appointment, Review
from .serializers import (
    SpecializationSerializer, DoctorSerializer,
    PatientSerializer, AppointmentSerializer, ReviewSerializer,
)


class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve specializations."""
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve doctors with filtering and search."""
    queryset = Doctor.objects.filter(is_available=True).select_related('specialization')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['name', 'qualification', 'specialization__name']
    ordering_fields = ['rating', 'experience_years', 'consultation_fee']
    ordering = ['-rating']

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """GET /api/doctors/{id}/reviews/ — all reviews for a doctor."""
        doctor = self.get_object()
        reviews = Review.objects.filter(
            appointment__doctor=doctor
        ).select_related('appointment__patient')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        """GET /api/doctors/{id}/available_slots/?date=YYYY-MM-DD"""
        doctor = self.get_object()
        date = request.query_params.get('date')
        if not date:
            return Response(
                {'error': 'date query param required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booked = Appointment.objects.filter(
            doctor=doctor, date=date
        ).exclude(status='Cancelled').values_list('time', flat=True)
        booked_times = [str(t) for t in booked]
        return Response({'date': date, 'booked_slots': booked_times})


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD for patients. Patients can only access their own record."""
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD for appointments. Patients see only their own."""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'doctor', 'date']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['-date', '-time']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all().select_related('patient', 'doctor')
        try:
            patient = user.patient
            return Appointment.objects.filter(
                patient=patient
            ).select_related('patient', 'doctor')
        except Patient.DoesNotExist:
            return Appointment.objects.none()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/appointments/{id}/cancel/"""
        appointment = self.get_object()
        if appointment.status not in ['Pending', 'Confirmed']:
            return Response(
                {'error': 'Only pending or confirmed appointments can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'Cancelled'
        appointment.save()
        return Response({'status': 'Appointment cancelled successfully.'})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """POST /api/appointments/{id}/confirm/ — admin only."""
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        appointment = self.get_object()
        appointment.status = 'Confirmed'
        appointment.save()
        return Response({'status': 'Appointment confirmed.'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """POST /api/appointments/{id}/complete/ — admin only."""
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        appointment = self.get_object()
        appointment.status = 'Completed'
        appointment.save()
        return Response({'status': 'Appointment marked as completed.'})


class ReviewViewSet(viewsets.ModelViewSet):
    """Create and list reviews for completed appointments."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['appointment__doctor']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Review.objects.all().select_related(
                'appointment__patient', 'appointment__doctor'
            )
        try:
            return Review.objects.filter(
                appointment__patient=user.patient
            ).select_related('appointment__patient', 'appointment__doctor')
        except Patient.DoesNotExist:
            return Review.objects.none()

    def perform_create(self, serializer):
        appointment = serializer.validated_data['appointment']

        # Only allow reviews on completed appointments owned by the user
        if appointment.status != 'Completed':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You can only review completed appointments.')

        if hasattr(appointment, 'review'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You have already reviewed this appointment.')

        review = serializer.save()

        # Recalculate doctor's average rating
        doctor = appointment.doctor
        avg = Review.objects.filter(
            appointment__doctor=doctor
        ).aggregate(Avg('rating'))['rating__avg']
        doctor.rating = round(avg, 2)
        doctor.save()
