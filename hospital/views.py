from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User, DoctorProfile, PatientProfile
from accounts.forms import AdminAddDoctorForm
from .models import (
    Appointment,
    MedicalRecord,
    Bill,
    Medicine,
    DispensedMedicine,
    LabTest,
    LabRequest,
)
from .forms import (
    AppointmentForm,
    MedicalRecordForm,
    AdminInvoiceForm,
    MedicineForm,
    DispenseMedicineForm,
    LabTestCatalogForm,
    LabRequestForm,
    LabResultForm,
)


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
    messages.success(request, f'Patient {patient.user.get_full_name()} has been approved to log in.')
    return redirect('admin_dashboard')


@login_required
def admin_create_invoice(request, appointment_id=None):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    unbilled_list = Appointment.objects.filter(bill__isnull=True)

    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if hasattr(appointment, 'bill'):
            messages.info(request, 'An invoice already exists for this appointment.')
            return redirect('print_invoice', bill_id=appointment.bill.id)
    else:
        appointment = None

    if request.method == 'POST':
        selected_appt_id = request.POST.get('appointment_id') or appointment_id
        appointment = get_object_or_404(Appointment, id=selected_appt_id)
        form = AdminInvoiceForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.appointment = appointment
            bill.save()
            messages.success(request, f'Invoice #AHC-{bill.id:04d} generated by Admin.')
            return redirect('print_invoice', bill_id=bill.id)
    else:
        if appointment:
            dispensed_items = appointment.dispensed_medicines.all()
            pharmacy_total = sum(item.subtotal for item in dispensed_items)
            lab_total = sum(req.test.cost for req in appointment.lab_requests.all())
            form = AdminInvoiceForm(initial={
                'consultation_fee': appointment.doctor.consultation_fee,
                'medication_charges': pharmacy_total + lab_total,
            })
        else:
            form = AdminInvoiceForm()

    return render(request, 'hospital/admin_create_invoice.html', {
        'form': form,
        'appointment': appointment,
        'unbilled_list': unbilled_list,
    })


@login_required
def mark_bill_paid(request, bill_id):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    bill = get_object_or_404(Bill, id=bill_id)
    bill.is_paid = True
    bill.save()
    messages.success(request, f'Bill #{bill.id} marked as Paid.')
    return redirect('admin_dashboard')


# --- PHARMACY & INVENTORY VIEWS ---

@login_required
def pharmacy_inventory(request):
    if request.user.role not in [User.Role.ADMIN, User.Role.DOCTOR] and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    medicines = Medicine.objects.all()
    if request.method == 'POST':
        if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
            messages.error(request, 'Only Hospital Administrators can add new medicines to inventory.')
            return redirect('pharmacy_inventory')
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added to pharmacy inventory.')
            return redirect('pharmacy_inventory')
    else:
        form = MedicineForm()

    return render(request, 'hospital/pharmacy_inventory.html', {
        'medicines': medicines,
        'form': form,
    })


@login_required
def restock_medicine(request, medicine_id):
    if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        added_qty = int(request.POST.get('added_qty', 0))
        if added_qty > 0:
            medicine.stock_quantity += added_qty
            medicine.save()
            messages.success(request, f'Added {added_qty} units to {medicine.name}.')
    return redirect('pharmacy_inventory')


@login_required
def dispense_medicine(request, appointment_id):
    if request.user.role not in [User.Role.ADMIN, User.Role.DOCTOR] and not request.user.is_superuser:
        return redirect('dashboard_redirect')

