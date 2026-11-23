from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from .models import Ward, Admission
from .forms import WardForm, AdmissionForm


@login_required
def ward_management(request):
    if request.user.role not in [User.Role.ADMIN, User.Role.DOCTOR] and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    wards = Ward.objects.all()
    active_admissions = Admission.objects.filter(is_discharged=False).order_by('-admitted_at')
    past_admissions = Admission.objects.filter(is_discharged=True).order_by('-discharged_at')[:10]

    ward_form = WardForm()
    admit_form = AdmissionForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_ward':
            if request.user.role != User.Role.ADMIN and not request.user.is_superuser:
                messages.error(request, 'Only Hospital Administrators can create wards.')
                return redirect('ward_management')
            ward_form = WardForm(request.POST)
            if ward_form.is_valid():
                ward_form.save()
                messages.success(request, 'New hospital ward created.')
                return redirect('ward_management')

        elif action == 'admit_patient':
            admit_form = AdmissionForm(request.POST)
            if admit_form.is_valid():
                admission = admit_form.save()
                messages.success(
                    request,
                    f"{admission.patient} admitted to {admission.ward.name} (Bed {admission.bed_number})."
                )
                return redirect('ward_management')

    return render(request, 'hospital/ward_management.html', {
        'wards': wards,
        'active_admissions': active_admissions,
        'past_admissions': past_admissions,
        'ward_form': ward_form,
        'admit_form': admit_form,
    })


@login_required
def discharge_patient(request, admission_id):
    if request.user.role not in [User.Role.ADMIN, User.Role.DOCTOR] and not request.user.is_superuser:
        return redirect('dashboard_redirect')

    admission = get_object_or_404(Admission, id=admission_id)

    if admission.is_discharged:
        messages.info(request, f"{admission.patient} has already been discharged from {admission.ward.name}.")
        return redirect('ward_management')

    admission.is_discharged = True
    admission.discharged_at = timezone.now()
    admission.save()

    messages.success(
        request,
        f"{admission.patient} discharged from {admission.ward.name}. Total stay: {admission.days_admitted} day(s) — KES {admission.total_ward_cost}."
    )
    return redirect('ward_management')
