# SIGCIM — Sistema de Gestión de Citas Médicas

A web-based medical appointment management system built with Django and PostgreSQL.

## Stack

- **Backend:** Python 3.12 · Django 5.0
- **Database:** PostgreSQL
- **Frontend:** Django Templates · Vanilla CSS (no frameworks)

## Features

- Role-based authentication (staff login)
- Dashboard with live stats and today's schedule
- Full appointment lifecycle: create → confirm → complete → medical record
- Patient registry with appointment history
- Doctor directory with specialty management
- Schedule conflict foundations via `Schedule` model
- Medical records attached to completed appointments

## Setup

```bash
git clone <repo>
cd sigcim
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a PostgreSQL database:
```sql
CREATE DATABASE sigcim_db;
CREATE USER sigcim_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sigcim_db TO sigcim_user;
```

Update `sigcim/settings.py` with your DB credentials, then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://localhost:8000` — log in and start scheduling.

## Project structure

```
sigcim/
├── appointments/
│   ├── models.py       # Specialty, Doctor, Patient, Schedule, Appointment, MedicalRecord
│   ├── views.py        # All views — dashboard, CRUD, detail pages
│   ├── forms.py        # ModelForms with validation
│   ├── urls.py         # URL routing
│   ├── admin.py        # Admin panel configuration
│   └── templates/
│       └── appointments/
│           ├── base.html
│           ├── login.html
│           ├── dashboard.html
│           ├── appointment_list.html
│           ├── appointment_detail.html
│           ├── appointment_form.html
│           ├── appointment_confirm_cancel.html
│           ├── patient_list.html
│           ├── patient_detail.html
│           └── doctor_list.html
├── static/
│   └── css/
│       └── main.css
├── sigcim/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Data models

| Model | Key fields |
|---|---|
| `Specialty` | name |
| `Doctor` | user (1:1), specialty, license_number, phone |
| `Patient` | user (1:1), date_of_birth, blood_type, insurance_number |
| `Schedule` | doctor, day_of_week, start_time, end_time, slot_duration |
| `Appointment` | patient, doctor, scheduled_at, status, reason |
| `MedicalRecord` | appointment (1:1), diagnosis, treatment, prescription |
