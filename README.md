# AYUNDA HEALTH CENTER — Hospital Management System

A full-stack, role-based **Hospital Management System** built with **Django**, **SQLite**, **HTML5**, and **Pure CSS** for **AYUNDA HEALTH CENTER** (Homa Bay Town, Homa Bay County, Kenya). Designed for real-world outpatient and inpatient healthcare operations, the platform coordinates patient onboarding, doctor consultations, confidential electronic medical records (EMR), pharmacy inventory, laboratory diagnostics, Admin-issued stamped invoices, and Safaricom M-Pesa payments.

---

## Table of Contents
1. [Core Modules & Features](#core-modules--features)
2. [Planned & Upcoming Integrations](#planned--upcoming-integrations)
3. [Role-Based Workflows](#role-based-workflows)
4. [Tech Stack & Architecture](#tech-stack--architecture)
5. [Folder Structure](#folder-structure)
6. [Database Schema Overview](#database-schema-overview)
7. [Installation & Local Setup](#installation--local-setup)
8. [M-Pesa Daraja API Configuration](#mpesa-daraja-api-configuration)
9. [Facility Contact Details](#facility-contact-details)

---

## Core Modules & Features

### 1. Multi-Portal Authentication & Access Control
* **Dedicated Role Portals:** Separate sign-in endpoints for **Patients** (`/accounts/login/patient/`), **Doctors / Medical Staff** (`/accounts/login/doctor/`), and **Hospital Administrators** (`/accounts/login/admin/`).
* **Admin-Controlled Doctor Onboarding:** Doctors cannot self-register publicly; only a Hospital Administrator can create and verify doctor credentials.
* **Patient Registration & Approval:** Patients register online with biodata (date of birth, blood group, emergency contact, address) and remain pending until approved by an Administrator.
* **Strict Record Privacy:** Clinical diagnoses, prescriptions, and doctor notes are strictly restricted to **Doctors** and **Administrators**.

### 2. Outpatient Appointments & Consultations
* Approved patients browse verified specialists and book appointments by date, time slot, and symptoms.
* Doctors manage their daily queue (`Pending` → `Approved` → `Completed` / `Cancelled`) and record clinical diagnoses and prescriptions.

### 3. Pharmacy & Medicine Inventory Management
* Real-time stock tracking by medicine name, therapeutic category, unit price (KES), stock count, and expiry date.
* Visual **Low Stock** badges when inventory drops to 10 units or fewer.
* Administrator restocking controls and direct dispensing workflows that automatically deduct stock quantities upon issuance.

### 4. Laboratory Diagnostics & Test Catalog
* Admin-managed catalog of clinical laboratory tests and standard pricing (KES).
* Doctors order lab tests per patient visit and record diagnostic test results directly against the consultation.

### 5. Admin-Issued Printable Invoices & Official Seal
* **Admin-Only Billing Control:** Only the Hospital Administrator generates and issues official invoices—automatically aggregating consultation fees, laboratory tests, and dispensed pharmacy items.
* **Print & PDF Ready (`@media print`):** Dedicated receipt layout that hides navigation and footer elements during printing and displays an official **AYUNDA HEALTH CENTER** tilted ink stamp with a dynamic date and **APPROVED** seal.

---

## Planned & Upcoming Integrations

* **Safaricom M-Pesa Daraja API (Lipa Na M-Pesa Online / STK Push):**
  * Trigger instant M-Pesa PIN prompts directly to a patient's Safaricom line from any unpaid invoice.
  * Automated JSON webhook callback (`/mpesa/callback/`) to verify payments, mark invoices as **PAID**, and stamp the official M-Pesa Receipt Number (e.g., `SLK89X2P1Q`) onto the hospital receipt.
* **Inpatient Ward & Bed Allocation:**
  * Track general, maternity, pediatric, and private wards, real-time bed occupancy, patient admission dates, and daily ward charges.
* **Automated Patient Notifications:**
  * SMS/Email alerts upon patient account approval, appointment confirmation, and invoice issuance.

---

## Role-Based Workflows

| Role | Permissions & Capabilities |
| :--- | :--- |
| **Hospital Administrator** | Full system oversight; registers new doctors; approves pending patient accounts; manages pharmacy stock & restocking; maintains lab test catalog; generates official stamped invoices; marks bills paid. |
| **Doctor (Medical Staff)** | Views assigned appointments; approves/cancels visits; orders lab tests & enters results; records confidential diagnoses & prescriptions; dispenses pharmacy medications. |
| **Patient** | Registers account; books appointments with approved doctors; views appointment statuses; views and prints itemized hospital invoices; initiates M-Pesa payments. |

---

## Tech Stack & Architecture

* **Backend Framework:** Python 3, Django
* **Database:** SQLite3 (`db.sqlite3` built-in relational database)
* **Frontend:** Semantic HTML5, Modular External CSS3 (`style.css` & `footer.css`), Inline Clinical SVG Icons
* **External APIs:** Safaricom Daraja REST API (OAuth 2.0 + STK Push) via `requests`

---

## Folder Structure

```text
HOSPITAL_MANAGEMENT/
├── accounts/                   # Custom User model, Doctor/Patient profiles, role login portals
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/                     # Global settings, root URLs, WSGI/ASGI entrypoints
│   ├── settings.py
│   └── urls.py
├── hospital/                   # Core clinical workflows, pharmacy, labs, billing, M-Pesa
│   ├── admin.py
│   ├── extra_views.py          # Invoice, pharmacy, and laboratory views
│   ├── forms.py
│   ├── models.py
│   ├── mpesa.py                # Daraja OAuth & STK Push helper (upcoming)
│   ├── mpesa_views.py          # Payment initiation & callback handler (upcoming)
│   ├── urls.py
│   └── views.py
├── static/
│   └── css/
│       ├── style.css           # Clinical teal & navy UI design system
│       └── footer.css          # Footer, printable invoice, and official stamp CSS
├── templates/
│   ├── base.html
│   ├── accounts/               # Portal selector, role login forms, patient sign-up
│   └── hospital/               # Landing page, dashboards, pharmacy, labs, invoices
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## Database Schema Overview

* **`accounts.User`**: Extends `AbstractUser` with `role` (`ADMIN`, `DOCTOR`, `PATIENT`) and `phone_number`.
* **`accounts.DoctorProfile`**: `OneToOne` to `User`; stores `specialization`, `license_number`, `consultation_fee`, and `is_approved`.
* **`accounts.PatientProfile`**: `OneToOne` to `User`; stores `date_of_birth`, `blood_group`, `emergency_contact`, `address`, and `is_approved`.
* **`hospital.Appointment`**: Links `PatientProfile` and `DoctorProfile` with `appointment_date`, `time_slot`, `symptoms`, and `status`.
* **`hospital.MedicalRecord`**: `OneToOne` to `Appointment`; stores confidential `diagnosis`, `prescription`, and `doctor_notes`.
* **`hospital.Medicine` & `hospital.DispensedMedicine`**: Tracks pharmacy inventory and itemized drugs issued per appointment.
* **`hospital.LabTest` & `hospital.LabRequest`**: Tracks available diagnostic tests, per-visit requests, and clinical result notes.
* **`hospital.Bill`**: `OneToOne` to `Appointment`; calculates `consultation_fee + medication_charges`, tracks `is_paid`, and stores M-Pesa transaction metadata.

---

## Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd HOSPITAL_MANAGEMENT
   ```

2. **Create and activate a virtual environment:**
   * **Windows (Command Prompt / PowerShell):**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Hospital Administrator (Superuser):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0`.

---

## M-Pesa Daraja API Configuration

To enable live or sandbox M-Pesa STK Push payments:
1. Obtain your **Consumer Key**, **Consumer Secret**, and **Passkey** from the [Safaricom Developer Portal](https://safaricom.co.ke).
2. Configure the credentials in `config/settings.py`:
   ```python
   MPESA_ENVIRONMENT = 'sandbox'  # Use 'production' in live deployment
   MPESA_CONSUMER_KEY = 'your_consumer_key'
   MPESA_CONSUMER_SECRET = 'your_consumer_secret'
   MPESA_SHORTCODE = '174379'
   MPESA_PASSKEY = 'your_daraja_passkey'
   MPESA_CALLBACK_URL = 'https://<your-public-domain-or-ngrok>/mpesa/callback/'
   ```
3. When testing locally, expose port `8000` using **ngrok** (`ngrok http 8000`) and update `MPESA_CALLBACK_URL` and `ALLOWED_HOSTS` with your HTTPS ngrok URL.

---

## Facility Contact Details

* **Hospital Name:** AYUNDA HEALTH CENTER
* **Location:** Homa Bay Town, Homa Bay County, Kenya
* **24/7 Emergency & Ambulance Desk:** `+254796943289`
