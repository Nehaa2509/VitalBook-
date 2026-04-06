from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from .models import Doctor, Patient, Appointment, Specialization, Review, ContactMessage, Billing, Prescription, Payment, OTPVerification
from django.contrib.auth.models import User
from . import email_utils
from . import otp_utils
import qrcode
import io
import os
import uuid
from django.core.files.base import ContentFile


def generate_qr_code(appointment):
    """Generate a QR code for appointment check-in containing appointment details."""
    qr_data = (
        f"VITALBOOK\n"
        f"Appointment ID: {appointment.id}\n"
        f"Patient: {appointment.patient.name}\n"
        f"Doctor: Dr. {appointment.doctor.name}\n"
        f"Date: {appointment.date.strftime('%d/%m/%Y')}\n"
        f"Time: {appointment.time.strftime('%I:%M %p')}"
    )
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B3B60", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    filename = f'qr_appointment_{appointment.id}.png'
    appointment.qr_code.save(filename, ContentFile(buffer.read()), save=True)


def send_booking_email(appointment):
    """Send a confirmation email to the patient after booking."""
    try:
        subject = f'VITALBOOK - Appointment Confirmation (#{appointment.id})'
        message = (
            f"Dear {appointment.patient.name},\n\n"
            f"Your appointment has been booked successfully!\n\n"
            f"Details:\n"
            f"  Doctor: Dr. {appointment.doctor.name} ({appointment.doctor.specialization.name})\n"
            f"  Date: {appointment.date.strftime('%d/%m/%Y')}\n"
            f"  Time: {appointment.time.strftime('%I:%M %p')}\n"
            f"  Consultation Fee: ₹{appointment.doctor.consultation_fee}\n\n"
            f"Please arrive 15 minutes before your scheduled time.\n"
            f"You can use the QR code in your dashboard for quick check-in.\n\n"
            f"Cancellation Policy: Free cancellation within 24 hours of booking. "
            f"A ₹500 cancellation fee applies after 24 hours.\n\n"
            f"Thank you for choosing VITALBOOK.\n"
            f"📞 +91 98765 43210\n"
        )
        send_mail(
            subject,
            message,
            django_settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Silently fail - email is a nice-to-have, not critical


def home(request):
    specializations = Specialization.objects.all()[:6]
    top_doctors = Doctor.objects.filter(is_available=True).order_by('-rating')[:3]
    total_doctors = Doctor.objects.filter(is_available=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'specializations': specializations,
        'top_doctors': top_doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    }
    return render(request, 'appointment/home.html', context)


def about(request):
    return render(request, 'appointment/about.html')


def services(request):
    specializations = Specialization.objects.all()
    return render(request, 'appointment/services.html', {'specializations': specializations})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'appointment/contact.html')


def doctor_list(request):
    # Annotate doctors with review statistics
    doctors = Doctor.objects.filter(is_available=True).annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    )
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialization__name__icontains=search_query) |
            Q(qualification__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    # Filter by specialization
    specialization_id = request.GET.get('specialization', '')
    if specialization_id:
        doctors = doctors.filter(specialization__id=specialization_id)
    
    # Filter by consultation fee range
    min_fee = request.GET.get('min_fee', '')
    max_fee = request.GET.get('max_fee', '')
    if min_fee:
        try:
            doctors = doctors.filter(consultation_fee__gte=float(min_fee))
        except ValueError:
            pass
    if max_fee:
        try:
            doctors = doctors.filter(consultation_fee__lte=float(max_fee))
        except ValueError:
            pass
    
    # Filter by minimum rating
    min_rating = request.GET.get('min_rating', '')
    if min_rating:
        try:
            # Use the pre-calculated rating field or annotated avg_rating
            doctors = doctors.filter(
                Q(rating__gte=float(min_rating)) | Q(avg_rating__gte=float(min_rating))
            )
        except ValueError:
            pass
    
    # Filter by availability (day of week)
    availability = request.GET.get('availability', '')
    if availability:
        doctors = doctors.filter(available_days__icontains=availability)
    
    # Filter by experience
    min_experience = request.GET.get('min_experience', '')
    if min_experience:
        try:
            doctors = doctors.filter(experience_years__gte=int(min_experience))
        except ValueError:
            pass
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'name')
    sort_options = {
        'name': 'name',
        'fee_low': 'consultation_fee',
        'fee_high': '-consultation_fee',
        'rating': '-rating',
        'experience': '-experience_years',
        'reviews': '-total_reviews',
    }
    doctors = doctors.order_by(sort_options.get(sort_by, 'name'))
    
    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all()
    
    # Check if today is available for each doctor
    today = timezone.now().strftime('%A')[:3]  # Get first 3 letters (Mon, Tue, etc.)
    
    context = {
        'doctors': doctors,
        'specializations': specializations,
        'search_query': search_query,
        'selected_specialization': specialization_id,
        'selected_min_fee': min_fee,
        'selected_max_fee': max_fee,
        'selected_min_rating': min_rating,
        'selected_availability': availability,
        'selected_min_experience': min_experience,
        'sort_by': sort_by,
        'total_results': doctors.count(),
        'today': today,
    }
    return render(request, 'appointment/doctor_list.html', context)


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).select_related('patient')[:5]
    total_reviews = Review.objects.filter(doctor=doctor).count()
    avg_rating = doctor.rating
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
    }
    return render(request, 'appointment/doctor_detail.html', context)


def register(request):
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '')
        confirm_pw = request.POST.get('confirm_password', '')
        name       = request.POST.get('name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        dob        = request.POST.get('date_of_birth', '').strip()
        gender     = request.POST.get('gender', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        address    = request.POST.get('address', '').strip()

        # Keep form data so user doesn't retype on error
        form_data = {
            'username': username, 'email': email, 'name': name,
            'phone': phone, 'dob': dob, 'gender': gender,
            'blood_group': blood_group, 'address': address,
        }

        # ── Required field checks ──────────────────────────────────────────
        errors = []
        if not name:
            errors.append('Full Name is required.')
        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email is required.')
        if not phone:
            errors.append('Phone number is required.')
        if not password:
            errors.append('Password is required.')
        if not gender:
            errors.append('Please select your Gender.')
        if not blood_group:
            errors.append('Please select your Blood Group.')
        if not address:
            errors.append('Address is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'appointment/register.html', {'form_data': form_data})

        # ── Password checks ───────────────────────────────────────────────
        if password != confirm_pw:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'appointment/register.html', {'form_data': form_data})

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'appointment/register.html', {'form_data': form_data})

        # ── Uniqueness checks ─────────────────────────────────────────────
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken. Please choose another.')
            return render(request, 'appointment/register.html', {'form_data': form_data})

        if User.objects.filter(email=email).exists():
            messages.error(request, f'An account with email "{email}" already exists. Please login instead.')
            return render(request, 'appointment/register.html', {'form_data': form_data})

        # ── DOB validation (optional field but must be valid if given) ────
        import datetime as dt
        dob_obj = None
        if dob:
            try:
                dob_obj = dt.date.fromisoformat(dob)
                if dob_obj > dt.date.today():
                    messages.error(request, 'Date of Birth cannot be a future date.')
                    return render(request, 'appointment/register.html', {'form_data': form_data})
                if dob_obj.year < 1900:
                    messages.error(request, 'Please enter a valid Date of Birth.')
                    return render(request, 'appointment/register.html', {'form_data': form_data})
            except ValueError:
                messages.error(request, 'Invalid Date of Birth format.')
                return render(request, 'appointment/register.html', {'form_data': form_data})

        # ── Create user (inactive until OTP) ─────────────────────────────
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        Patient.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            date_of_birth=dob_obj,
            gender=gender,
            blood_group=blood_group,
            address=address,
        )

        # ── OTP: prefer SMS if phone given, fall back to email ────────────
        otp_method = 'mobile' if phone else 'email'
        otp_obj = OTPVerification.objects.create(user=user, otp_type=otp_method)
        otp = otp_obj.generate_otp()

        if otp_method == 'mobile':
            sms_sent = otp_utils.send_mobile_otp(phone, otp)
            if not sms_sent:
                otp_utils.send_email_otp(user, otp)
            channel_msg = 'phone number'
        else:
            otp_utils.send_email_otp(user, otp)
            channel_msg = 'email'

        request.session['user_id']    = user.id
        request.session['user_email'] = user.email

        messages.success(
            request,
            f'Registration successful! A 6-digit OTP has been sent to your {channel_msg}. '
            f'Please verify to activate your account.'
        )
        return redirect('verify_otp')

    return render(request, 'appointment/register.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'appointment/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@login_required
def profile(request):
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.gender = request.POST.get('gender')
        patient.blood_group = request.POST.get('blood_group')
        patient.address = request.POST.get('address')
        patient.emergency_contact = request.POST.get('emergency_contact')
        patient.medical_history = request.POST.get('medical_history')

        # Server-side DOB validation — safety net behind JS checks
        dob_str = request.POST.get('date_of_birth')
        if dob_str:
            try:
                import datetime as dt
                dob = dt.date.fromisoformat(dob_str)
                if dob > dt.date.today():
                    messages.error(request, 'Date of Birth cannot be a future date!')
                    return render(request, 'appointment/profile.html', {'patient': patient})
                if dob.year < 1900:
                    messages.error(request, 'Please enter a valid Date of Birth.')
                    return render(request, 'appointment/profile.html', {'patient': patient})
                patient.date_of_birth = dob
            except ValueError:
                messages.error(request, 'Invalid date format for Date of Birth.')
                return render(request, 'appointment/profile.html', {'patient': patient})
        else:
            patient.date_of_birth = None

        patient.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'appointment/profile.html', {'patient': patient})


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        date = request.POST['date']
        time = request.POST['time']
        reason = request.POST.get('reason', '')
        symptoms = request.POST.get('symptoms', '')
        
        # Check if slot is already booked
        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exclude(status='Cancelled').exists():
            messages.error(request, 'This time slot is already booked. Please choose another time.')
            return redirect('book_appointment', doctor_id=doctor_id)
        
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason,
            symptoms=symptoms,
            status='Pending'  # Keep as Pending until payment
        )

        # Generate QR code for check-in
        try:
            generate_qr_code(appointment)
        except Exception:
            pass  # QR code generation is non-critical

        # Create a Billing record for the consultation fee
        Billing.objects.create(
            appointment=appointment,
            total_amount=doctor.consultation_fee,
            billing_type='Consultation',
            is_paid=False,
        )

        messages.success(request, 'Appointment created! Please complete the payment to confirm.')
        return redirect('checkout', appointment_id=appointment.id)
    
    # Get booked slots for this doctor
    today = timezone.now().date()
    booked_slots = Appointment.objects.filter(
        doctor=doctor,
        date__gte=today
    ).exclude(status='Cancelled').values_list('date', 'time')
    
    context = {
        'doctor': doctor,
        'booked_slots': list(booked_slots),
        'today': today.isoformat(),
    }
    return render(request, 'appointment/book_appointment.html', context)


@login_required
def my_appointments(request):
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    # Filter appointments
    status_filter = request.GET.get('status', 'all')
    appointments = Appointment.objects.filter(patient=patient)
    
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    # Separate upcoming and past appointments
    today = timezone.now().date()
    upcoming = appointments.filter(date__gte=today).exclude(status__in=['Completed', 'Cancelled'])
    past = appointments.filter(Q(date__lt=today) | Q(status__in=['Completed', 'Cancelled']))
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'status_filter': status_filter,
    }
    return render(request, 'appointment/my_appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure patient can only view their own appointments
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('my_appointments')
    
    # Check if review exists
    has_review = hasattr(appointment, 'review')

    # Get billing records
    billings = appointment.billings.all()

    # Get prescription if exists
    prescription_record = None
    try:
        prescription_record = appointment.prescription_record
    except Prescription.DoesNotExist:
        pass
    
    context = {
        'appointment': appointment,
        'has_review': has_review,
        'billings': billings,
        'prescription_record': prescription_record,
    }
    return render(request, 'appointment/appointment_detail.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient.user == request.user:
        if appointment.status in ['Pending', 'Confirmed']:
            cancellation_fee = 0

            # Check if more than 24 hours have passed since booking
            if not appointment.can_cancel_free():
                cancellation_fee = 500  # ₹500 cancellation fee
                appointment.cancellation_fee_applied = cancellation_fee

                # Create a billing record for the cancellation fee
                Billing.objects.create(
                    appointment=appointment,
                    total_amount=cancellation_fee,
                    billing_type='Cancellation Fee',
                    is_paid=False,
                )

            appointment.status = 'Cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.save()
            
            # Send cancellation emails
            email_utils.send_appointment_cancelled(appointment, cancelled_by='patient')

            if cancellation_fee > 0:
                messages.warning(
                    request,
                    f'Appointment cancelled. A cancellation fee of ₹{cancellation_fee} has been applied '
                    f'as the cancellation was made after the 24-hour free cancellation window.'
                )
            else:
                messages.success(request, 'Appointment cancelled successfully within the free cancellation window!')
        else:
            messages.error(request, 'This appointment cannot be cancelled.')
    else:
        messages.error(request, 'You do not have permission to cancel this appointment.')
    
    return redirect('my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        new_date = request.POST['date']
        new_time = request.POST['time']
        
        # Check if new slot is available
        if Appointment.objects.filter(
            doctor=appointment.doctor,
            date=new_date,
            time=new_time
        ).exclude(id=appointment_id).exclude(status='Cancelled').exists():
            messages.error(request, 'This time slot is already booked. Please choose another time.')
            return redirect('reschedule_appointment', appointment_id=appointment_id)
        
        appointment.date = new_date
        appointment.time = new_time
        appointment.status = 'Pending'
        appointment.save()
        
        messages.success(request, 'Appointment rescheduled successfully!')
        return redirect('my_appointments')
    
    context = {
        'appointment': appointment,
        'today': timezone.now().date().isoformat(),
    }
    return render(request, 'appointment/reschedule_appointment.html', context)


@login_required
def add_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to review this appointment.')
        return redirect('my_appointments')
    
    if appointment.status != 'Completed':
        messages.error(request, 'You can only review completed appointments.')
        return redirect('my_appointments')
    
    if hasattr(appointment, 'review'):
        messages.error(request, 'You have already reviewed this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST.get('comment', '')
        
        # Create review
        Review.objects.create(
            appointment=appointment,
            doctor=appointment.doctor,
            patient=appointment.patient,
            rating=rating,
            comment=comment
        )
        
        # Update doctor's average rating
        doctor = appointment.doctor
        reviews = Review.objects.filter(doctor=doctor)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.rating = round(avg_rating, 2) if avg_rating else 0
        doctor.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('my_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointment/add_review.html', context)


@login_required
def submit_review(request, appointment_id):
    """AJAX endpoint to submit review."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return JsonResponse({'status': 'error', 'message': 'Invalid rating'}, status=400)
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Permission check
        if appointment.patient.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Status check
        if appointment.status != 'Completed':
            return JsonResponse({'status': 'error', 'message': 'Can only review completed appointments'}, status=400)
        
        # Duplicate check
        if hasattr(appointment, 'review'):
            return JsonResponse({'status': 'error', 'message': 'Already reviewed'}, status=400)
        
        # Create review
        review = Review.objects.create(
            appointment=appointment,
            doctor=appointment.doctor,
            patient=appointment.patient,
            rating=int(rating),
            comment=comment
        )
        
        # Update doctor's average rating
        doctor = appointment.doctor
        reviews = Review.objects.filter(doctor=doctor)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.rating = round(avg_rating, 2) if avg_rating else 0
        doctor.save()
        
        # Send thank you email
        email_utils.send_review_thankyou(review)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Review submitted successfully',
            'new_rating': float(doctor.rating),
            'review_count': reviews.count()
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def doctor_reviews(request, doctor_id):
    """Display all reviews for a doctor."""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).select_related('patient', 'appointment')
    
    # Calculate rating distribution
    total_reviews = reviews.count()
    rating_distribution = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    
    # Calculate percentages
    rating_percentages = {}
    for rating, count in rating_distribution.items():
        rating_percentages[rating] = (count / total_reviews * 100) if total_reviews > 0 else 0
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'rating_percentages': rating_percentages,
        'avg_rating': doctor.rating,
    }
    
    return render(request, 'appointment/doctor_reviews.html', context)


def search_doctors(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.filter(is_available=True)
    
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__name__icontains=query) |
            Q(qualification__icontains=query)
        )
    
    context = {
        'doctors': doctors,
        'query': query,
    }
    return render(request, 'appointment/search_results.html', context)



@login_required
def checkout(request, appointment_id):
    """Display checkout page for payment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure patient can only checkout their own appointments
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('my_appointments')
    
    # Check if already paid
    if appointment.status == 'Confirmed' and appointment.payments.filter(payment_status='Completed').exists():
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
        'doctor': appointment.doctor,
        'amount': appointment.doctor.consultation_fee,
    }
    return render(request, 'appointment/checkout.html', context)


@login_required
def process_payment(request):
    """Process payment via AJAX and return JSON response."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        payment_method = data.get('payment_method')
        
        if not appointment_id or not payment_method:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Ensure patient can only pay for their own appointments
        if appointment.patient.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Generate unique booking ID
        booking_id = f"VB-{uuid.uuid4().hex[:8].upper()}"
        
        # Create payment record
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.doctor.consultation_fee,
            payment_status='Completed',
            payment_method=payment_method,
            transaction_id=booking_id,
            payment_date=timezone.now(),
        )
        
        # Update appointment status
        appointment.status = 'Confirmed'
        appointment.save()
        
        # Update billing record
        billing = appointment.billings.filter(billing_type='Consultation').first()
        if billing:
            billing.is_paid = True
            billing.save()
        
        # Send confirmation and payment receipt emails
        email_utils.send_appointment_confirmation(appointment)
        email_utils.send_payment_receipt(appointment, payment)
        
        return JsonResponse({
            'status': 'success',
            'booking_id': booking_id,
            'doctor_name': appointment.doctor.name,
            'appointment_date': appointment.date.strftime('%d %b, %Y'),
            'appointment_time': appointment.time.strftime('%I:%M %p'),
            'amount': str(appointment.doctor.consultation_fee),
            'payment_method': payment_method,
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def payment_success(request, appointment_id):
    """Handle successful payment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure patient can only access their own payment success page
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('my_appointments')
    
    # Get the latest payment for this appointment
    payment = appointment.payments.filter(payment_status='Processing').first()
    
    if payment:
        # Update payment status
        payment.payment_status = 'Completed'
        payment.payment_date = timezone.now()
        payment.save()
        
        # Update appointment status
        appointment.status = 'Confirmed'
        appointment.save()
        
        # Update billing record
        billing = appointment.billings.filter(billing_type='Consultation').first()
        if billing:
            billing.is_paid = True
            billing.save()
    
    context = {
        'appointment': appointment,
        'payment': payment,
    }
    return render(request, 'appointment/payment_success.html', context)


@login_required
def patient_dashboard(request):
    """Patient dashboard with appointments, stats, and quick actions."""
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    # Get all appointments for this patient
    all_appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'doctor__specialization')
    
    # Categorize appointments
    today = timezone.now().date()
    upcoming = all_appointments.filter(date__gte=today, status__in=['Pending', 'Confirmed']).order_by('date', 'time')
    completed = all_appointments.filter(status='Completed').order_by('-date', '-time')
    cancelled = all_appointments.filter(status='Cancelled').order_by('-date', '-time')
    
    # Calculate stats
    total_appointments = all_appointments.count()
    upcoming_count = upcoming.count()
    completed_count = completed.count()
    cancelled_count = cancelled.count()
    
    # Get payment history
    payments = Payment.objects.filter(
        appointment__patient=patient,
        payment_status='Completed'
    ).select_related('appointment', 'appointment__doctor').order_by('-payment_date')
    
    # Calculate total spent
    total_spent = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get reviews by this patient
    reviews = Review.objects.filter(patient=patient).select_related('doctor', 'appointment')
    
    # Get greeting based on time
    current_hour = timezone.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    context = {
        'patient': patient,
        'greeting': greeting,
        'total_appointments': total_appointments,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'upcoming_appointments': upcoming[:5],  # Show first 5
        'completed_appointments': completed[:5],  # Show first 5
        'cancelled_appointments': cancelled[:5],  # Show first 5
        'payments': payments[:10],  # Show last 10
        'total_spent': total_spent,
        'reviews': reviews,
    }
    return render(request, 'appointment/patient_dashboard.html', context)


@login_required
def update_profile(request):
    """Update patient profile information."""
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        # Update patient info
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.email = request.POST.get('email')
        patient.date_of_birth = request.POST.get('date_of_birth') or None
        patient.gender = request.POST.get('gender')
        patient.blood_group = request.POST.get('blood_group')
        patient.address = request.POST.get('address')
        patient.emergency_contact = request.POST.get('emergency_contact')
        patient.medical_history = request.POST.get('medical_history')
        patient.save()
        
        # Update user email
        request.user.email = patient.email
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_dashboard')
    
    return redirect('patient_dashboard')



@login_required
def doctor_dashboard(request):
    """Doctor dashboard with appointments, stats, and revenue."""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
    
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Appointment stats
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    today_appointments = Appointment.objects.filter(doctor=doctor, date=today).order_by('time')
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='Pending').count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='Completed').count()
    
    # Unique patients count
    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()
    
    # Revenue stats
    monthly_revenue = Payment.objects.filter(
        appointment__doctor=doctor,
        appointment__date__gte=this_month,
        payment_status='Completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_revenue = Payment.objects.filter(
        appointment__doctor=doctor,
        payment_status='Completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Reviews
    avg_rating = doctor.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = doctor.reviews.count()
    recent_reviews = doctor.reviews.select_related('patient', 'appointment').order_by('-created_at')[:5]
    
    # Recent appointments
    recent_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient').order_by('-date', '-time')[:10]
    
    # Pending requests
    pending_requests = Appointment.objects.filter(
        doctor=doctor,
        status='Pending'
    ).select_related('patient').order_by('date', 'time')[:10]
    
    # Weekly appointment chart data
    weekly_data = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Appointment.objects.filter(doctor=doctor, date=day).count()
        weekly_data.append({
            'day': day.strftime('%a'),
            'count': count,
            'date': day.strftime('%Y-%m-%d')
        })
    
    # Get greeting based on time
    current_hour = timezone.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    context = {
        'doctor': doctor,
        'greeting': greeting,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'total_patients': total_patients,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,
        'recent_appointments': recent_appointments,
        'pending_requests': pending_requests,
        'weekly_data': weekly_data,
    }
    return render(request, 'appointment/doctor_dashboard.html', context)


@login_required
def update_appointment_status(request, appointment_id):
    """AJAX endpoint to update appointment status."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in ['Confirmed', 'Completed', 'Cancelled']:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if user is the doctor for this appointment
        try:
            doctor = Doctor.objects.get(user=request.user)
            if appointment.doctor != doctor:
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        except Doctor.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Doctor profile not found'}, status=403)
        
        # Update status
        appointment.status = status
        if status == 'Cancelled':
            appointment.cancelled_at = timezone.now()
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Appointment marked as {status}',
            'status': status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def update_doctor_profile(request):
    """Update doctor profile information."""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        # Update doctor info
        doctor.name = request.POST.get('name')
        doctor.qualification = request.POST.get('qualification')
        doctor.experience_years = request.POST.get('experience_years')
        doctor.consultation_fee = request.POST.get('consultation_fee')
        doctor.available_days = request.POST.get('available_days')
        doctor.available_time = request.POST.get('available_time')
        doctor.phone = request.POST.get('phone')
        doctor.email = request.POST.get('email')
        doctor.bio = request.POST.get('bio')
        doctor.is_available = request.POST.get('is_available') == 'on'
        doctor.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')



def verify_otp(request):
    """Verify OTP for user registration."""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        
        try:
            otp_obj = OTPVerification.objects.filter(
                user=user,
                is_verified=False
            ).latest('created_at')
            
            if otp_obj.is_expired():
                messages.error(request, 'OTP expired. Please request a new one.')
            elif otp_obj.otp == entered_otp:
                # OTP is correct
                otp_obj.is_verified = True
                otp_obj.save()
                
                # Activate user account
                user.is_active = True
                user.save()
                
                # Send welcome email
                try:
                    patient = user.patient
                    email_utils.send_welcome_email(user, patient)
                except:
                    pass
                
                # Clear session
                del request.session['user_id']
                if 'user_email' in request.session:
                    del request.session['user_email']
                
                messages.success(request, 'Account verified successfully! You can now login.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
    
    context = {
        'user': user,
        'email': user.email
    }
    return render(request, 'appointment/verify_otp.html', context)


def resend_otp(request):
    """Resend OTP to user."""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
        
        # Create new OTP
        otp_obj = OTPVerification.objects.create(user=user, otp_type='email')
        otp = otp_obj.generate_otp()
        otp_utils.send_email_otp(user, otp)
        
        messages.success(request, 'New OTP sent to your email.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    except Exception as e:
        messages.error(request, 'Error sending OTP. Please try again.')
    
    return redirect('verify_otp')


@login_required
def download_prescription_pdf(request, appointment_id):
    """Generate and download a professional PDF prescription."""
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient__user=request.user  # patients can only download their own
    )
    prescription = Prescription.objects.filter(appointment=appointment).first()

    if not prescription:
        messages.error(request, 'No prescription found for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    from django.template.loader import get_template
    from xhtml2pdf import pisa

    template = get_template('appointment/prescription_pdf.html')
    context = {'appointment': appointment, 'prescription': prescription}
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    safe_name = f"Prescription_{appointment.patient.name.replace(' ', '_')}_{appointment.date}"
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    return response
