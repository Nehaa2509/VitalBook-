from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# DRF router for REST API
router = DefaultRouter()
router.register(r'specializations', api_views.SpecializationViewSet, basename='specialization')
router.register(r'doctors', api_views.DoctorViewSet, basename='doctor')
router.register(r'patients', api_views.PatientViewSet, basename='patient')
router.register(r'appointments', api_views.AppointmentViewSet, basename='appointment')
router.register(r'reviews', api_views.ReviewViewSet, basename='review')

urlpatterns = [
    # REST API
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),

    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Patient Dashboard
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/update/', views.update_profile, name='update_profile'),
    
    # Doctor Dashboard
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/update/', views.update_doctor_profile, name='update_doctor_profile'),
    path('appointments/<int:appointment_id>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    
    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('search/', views.search_doctors, name='search_doctors'),
    
    # Appointments
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    
    # Reviews
    path('review/<int:appointment_id>/', views.add_review, name='add_review'),
    path('review/submit/<int:appointment_id>/', views.submit_review, name='submit_review'),
    path('doctor/<int:doctor_id>/reviews/', views.doctor_reviews, name='doctor_reviews'),
    
    # Payment
    path('checkout/<int:appointment_id>/', views.checkout, name='checkout'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment-success/<int:appointment_id>/', views.payment_success, name='payment_success'),
    # path('receipt/download/<int:appointment_id>/', views.download_receipt, name='download_receipt'),
]
