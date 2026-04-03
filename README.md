# Hospital Appointment System

A complete web-based Hospital Appointment System built with Django, SQLite, HTML, CSS, and JavaScript.

## Features

### Patient Features
- User registration and login
- View available doctors by specialization
- Book appointments with doctors
- View appointment history
- Cancel appointments
- Real-time appointment status tracking

### Admin Features
- Manage doctors (add, edit, delete)
- View all appointments
- Approve or cancel appointments
- Filter appointments by status, date, and doctor

## Technology Stack

- **Backend**: Python 3.13, Django 6.0
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django built-in auth system

## Project Structure

```
hospital_project/
├── manage.py
├── db.sqlite3
├── hospital_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── appointment/
    ├── models.py          # Database models
    ├── views.py           # View logic
    ├── urls.py            # URL routing
    ├── admin.py           # Admin configuration
    ├── templates/
    │   └── appointment/
    │       ├── base.html
    │       ├── home.html
    │       ├── doctor_list.html
    │       ├── register.html
    │       ├── login.html
    │       ├── book_appointment.html
    │       └── my_appointments.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── script.js
```

## Setup Instructions

### 1. Activate Virtual Environment

**PowerShell:**
```powershell
.\activate.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Run Development Server

**Using script:**
```powershell
.\start_server.ps1
```

**Or manually:**
```bash
python manage.py runserver
```

### 3. Access the Application
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

### 4. Login Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

**Patient Accounts:**
- Usernames: `john_doe`, `jane_smith`, `bob_wilson`
- Password: `password123`

### 5. Populate Database (if needed)
```bash
python manage.py populate_data
```

## Usage Guide

### For Patients

1. **Register**: Create an account with your details
2. **Login**: Access your account
3. **Browse Doctors**: View available doctors and their specializations
4. **Book Appointment**: Select a doctor, choose date/time, and book
5. **Track Appointments**: View your appointment history and status

### For Admin

1. Login to admin panel at `/admin/`
2. Add doctors with their specializations and availability
3. Manage appointments (approve, cancel, mark completed)
4. View patient information

## Database Models

### Doctor
- Name
- Specialization
- Available time
- Email
- Phone

### Patient
- User (linked to Django User)
- Name
- Email
- Phone
- Address

### Appointment
- Patient (Foreign Key)
- Doctor (Foreign Key)
- Date
- Time
- Status (Pending/Confirmed/Completed/Cancelled)
- Reason
- Created timestamp

## Key Features Explained

### Authentication System
- Secure user registration and login
- Password validation
- Session management

### Appointment Booking
- Date validation (no past dates)
- Time selection
- Reason for visit
- Automatic status tracking

### Admin Dashboard
- Full CRUD operations for doctors
- Appointment management
- Search and filter capabilities

## Future Enhancements

- Email notifications for appointment confirmations
- SMS reminders
- Doctor availability calendar
- Payment integration
- Patient medical history
- Prescription management
- Video consultation feature

## Project Demonstration Tips

### For Viva/Interview

1. **Explain the flow**: Patient → Register → Login → Browse Doctors → Book → Track
2. **Database design**: Show ER diagram and relationships
3. **Security**: Explain authentication and CSRF protection
4. **Frontend**: Demonstrate responsive design and form validation
5. **Admin features**: Show how doctors and appointments are managed

### Key Points to Highlight

- MVC architecture (Django MVT pattern)
- Database normalization
- User authentication and authorization
- Form validation (client and server-side)
- RESTful URL design
- Responsive CSS design
- JavaScript for interactivity

## License

This is a student project for educational purposes.
