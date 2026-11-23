from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User, DoctorProfile, PatientProfile
from accounts.forms import AdminAddDoctorForm
from .models import Appointment, MedicalRecord, Bill
from .forms import AppointmentForm, MedicalRecordForm
from .notifications import send_patient_notification


def home(request):
    return render(request, 'hospital/home.html')


# --- PATIENT VIEWS ---

@login_required
def patient_dashboard(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('dashboard_redirect')

    patient = get_object_or_404(PatientProfile, user=request.user)
    if not patient.is_approved:
        messages.error(request, 'Your account requires Admin approval.')
        return redirect('logout')

    appointments = patient.appointments.all()
    bills = Bill.objects.filter(appointment__patient=patient).order_by('-generated_at')

    context = {
        'patient': patient,
        'appointments': appointments,
        'bills': bills,
    }
    return render(request, 'hospital/patient_dashboard.html', context)


@login_required
def book_appointment(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('dashboard_redirect')

    patient = get_object_or_404(PatientProfile, user=request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, 'Appointment booked! Awaiting doctor confirmation.')
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()

    return render(request, 'hospital/book_appointment.html', {'form': form})


# --- DOCTOR VIEWS ---

@login_required
def doctor_dashboard(request):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_redirect')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointments = doctor.appointments.all()

    context = {
        'doctor': doctor,
        'appointments': appointments,
    }
    return render(request, 'hospital/doctor_dashboard.html', context)


@login_required
def update_appointment_status(request, appointment_id, status):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_redirect')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if status in [Appointment.Status.APPROVED, Appointment.Status.CANCELLED]:
        appointment.status = status
        appointment.save()
        send_patient_notification(
            appointment.patient,
            subject=f"Appointment {status.title()}",
            message_body=f"Your appointment with {appointment.doctor} on {appointment.appointment_date} at {appointment.time_slot} has been {status.lower()}."
        )
        messages.success(request, f'Appointment marked as {status}.')

    return redirect('doctor_dashboard')


@login_required
def complete_consultation(request, appointment_id):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_redirect')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.appointment = appointment
            record.save()

            appointment.status = Appointment.Status.COMPLETED
            appointment.save()
            messages.success(request, 'Consultation completed and medical record saved. Ready for Admin billing.')
            return redirect('doctor_dashboard')
    else:
        form = MedicalRecordForm()

    return render(request, 'hospital/complete_consultation.html', {
        'form': form,
        'appointment': appointment
    })


# --- ADMIN VIEWS ---

@login_required
def admin_dashboard(request):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    doctors = DoctorProfile.objects.all()
    patients = PatientProfile.objects.all().order_by('-id')
    appointments = Appointment.objects.all()
    records = MedicalRecord.objects.all().order_by('-created_at')
    bills = Bill.objects.all().order_by('-generated_at')
    unbilled_appointments = Appointment.objects.filter(
        status__in=[Appointment.Status.APPROVED, Appointment.Status.COMPLETED],
        bill__isnull=True
    )

    context = {
        'doctors': doctors,
        'patients': patients,
        'appointments': appointments,
        'records': records,
        'bills': bills,
        'unbilled_appointments': unbilled_appointments,
    }
    return render(request, 'hospital/admin_dashboard.html', context)


@login_required
def admin_add_doctor(request):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AdminAddDoctorForm(request.POST)
        if form.is_valid():
            doctor_user = form.save()
            messages.success(request, f'Dr. {doctor_user.get_full_name()} added! They can now log in.')
            return redirect('admin_dashboard')
    else:
        form = AdminAddDoctorForm()

    return render(request, 'hospital/admin_add_doctor.html', {'form': form})


@login_required
def approve_patient(request, patient_id):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    patient = get_object_or_404(PatientProfile, id=patient_id)
    patient.is_approved = True
    patient.save()
    send_patient_notification(
        patient,
        subject="Patient Account Approved",
        message_body="Your patient account at AYUNDA HEALTH CENTER has been approved. You can now log in to book appointments and view your invoices."
    )
    messages.success(request, f'Patient {patient.user.get_full_name()} has been approved to log in.')
    return redirect('admin_dashboard')


@login_required
def mark_bill_paid(request, bill_id):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    bill = get_object_or_404(Bill, id=bill_id)
    bill.is_paid = True
    bill.save()
    messages.success(request, f'Bill #{bill.id} marked as Paid.')
    return redirect('admin_dashboard')


from .extra_views import *
