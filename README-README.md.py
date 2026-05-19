# EduSub - Substitute Teacher Platform
from nicegui.json import NiceGUIJSONResponse
from passlib.handlers.bcrypt import bcrypt
from starlette.datastructures import MultiDict

import main

browser-based platform for coordinating substitute teachers
    at Kindergarten and Primary school level (Grades 1-6).
BSc BIT - Advanced Programming SS26 - FHNW

## School Structure
KG1, KG2 - Kindergarten (free curriculm)
Grades 1-2 - German, Maths, LNMG, Textiles, Art, PE, Music
Grades 3-4 - + French
Grades 5-6 - +French, English

##Tech Stack
Fronted   NiceGUI (Vue.js / Quasar)
Backend   Python 3.14, OOP service classes
ORM       SQLalchemy 2.0 (no raw SQL)
Database  SQLite (edusub.db)
Auth      bcrypt + NiceGUI session storage
Tests     pytest

## Getting Started
cd EduSub_Project
.¨\venv\Scripts\Activate.ps1
python main.py
# Open http://localhost:8080

## Running Tests
pytest tests/ -v

## Key Features
- Role-based access: Admin and Teacher
- Unique staff number (LP-2026-XXXX) assigned on registration
- Subject list adapts per grade (French from G3, English from G5)
- Open requests auto-delated 12h before start if unaccepted
- Teacher profile page with editable subjects and bio

## Team
   Member A Auth, Login, Register, User model, database
   Member B Admin Dashboard, RequestService, auto-deletion
   Member C Teacher Dashboard, Profile, E2E test, README2


