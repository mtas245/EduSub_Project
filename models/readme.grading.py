#SubConnect
from docutils.nodes import substitution_definition
from fastapi import requests
from passlib.handlers.bcrypt import bcrypt

import database
import services
from models import teacher_dashboard
from models.application import status

> Substitute Teacher Coordination Platform
> Advanced Programming - BSc BIT - SS26

## Team Members

| Member | GitHub | Responsibility |
|--------|--------|----------------|
| Mamber A | uAhmet1907 | Authentication, User Model, Login/Register views |
| Member B | mtas245 | Admin Dashboard, substitute Requests Management |
| Member C | E-Ata | Teacher Dashboard, Application logic, README |

## Project Description

EduMatch is a browser-based platform bıilt with python and NiceGUI that
replaces informal WhatsApp-based substitute teacher coordination with a
structured, role-aware web application. Schools post absences, teachers apply,
and admins approve - all in one place.

## Tech Stack

- Fronted: NıceGUI (python-native, vue.js/quasar engine)
- Backend: python 3.11 with OOP service classes
- ORM: SQLALchemy 2.0 (no raw SQL)
- Database: SQLite (subconnect.db)
- Auth: bcrypt password hashing + NıceGUI session storage

## How to Run

'''bash
git clone https://github.com/YOUR_USERNAME/subconnect.git
cd subconnect
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py
# Open http://localhost:8080
'''

# User Stories

| ID | Role | Story |
|----|------|-------|
| US-01 | Admin | post a sustitute request with subject, date, grade level |
| US-02 | Admin | Approve or reject a teacher in a dashboard |
| US-03 | Admin | View all requests and their status in a dashboard |
| US-04 | Teacher | Browse all open substitute requests |
| US-05 | Teacher | Apply for an open request with one click |
| US-06 | Teacher | View own applications and approval status |
| US-07 | Any | Register and log in securely (bcrypt hashed password) |
| US-08 | Any | Be redirected to login if accessing a protected page |

## Project Structure

'''
subconnect/
├── main.py # App entry point, routes, route guard
├── database.py # SQLAlchemy engine and session
├── auth.py # Password hashing, login logic
├── models/
| ├── user.py # User model with Role enum
| ├── request.py # SubstituteRequest model
| └── application.py # Application model
├── services/
| ├── request_service.py # Admin business logic
| └── application_service.py # Teacher business logic
├── views/
| ├── login.py # Login page
| ├── register.py # Registration page
| ├── admin_dashboard.py # Admin dashboard
| └── teacher_dashboard.py # Teacher dashboard
├── subconnect.db # SQLite database (auto-created)
└── requirements.txt
'''
 ## Libraries Used

| Library | Version | Purpose |
|---------|---------|---------|
| nicegui | >=1.4 | Browser-based UI components |
| sqlalchemy | >=2.0 | ORM — database access without raw SQL |
| bcrypt | >=4.0 | Secure password hashing |
| python-dotenv | >=1.0 | Environment variable management |
| pytest | >=7.0 | Unit testing |

## Work Distribution

Member A: database.py, auth.py, models/user.py, views/login.py, views/register.py, main.py (routes + route guard)

Member B: Models/request.py, services/request_service.py, views/admin_dashboard.py

Member C: models/applications.py, services/application_service.py, views/teacher_dashboard.py, README.md

