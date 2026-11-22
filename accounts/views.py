from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PatientRegistrationForm
from .models import User


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Registration submitted! You will be able to log in once an Administrator approves your account.'
            )
            return redirect('patient_login')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Patient'})


def login_portal(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'accounts/login_portal.html')


def patient_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser or user.role != User.Role.PATIENT:
                messages.error(request, 'Access denied. Please use the Doctor or Admin login portal.')
                return redirect('patient_login')

            if not hasattr(user, 'patient_profile') or not user.patient_profile.is_approved:
                messages.error(request, 'Your patient account is still pending Administrator approval.')
                return redirect('patient_login')

            login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid patient username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'portal_title': 'Patient Login Portal',
        'portal_subtitle': 'Sign in to book appointments and check your billing status.',
        'is_patient': True,
    })


def doctor_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser or user.role != User.Role.DOCTOR:
                messages.error(request, 'Access denied. This portal is for registered Doctors only.')
                return redirect('doctor_login')

            login(request, user)
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid doctor username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'portal_title': 'Medical Staff (Doctor) Login',
        'portal_subtitle': 'Sign in to manage patient consultations, diagnoses, and prescriptions.',
        'is_patient': False,
    })


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not (user.is_superuser or user.role == User.Role.ADMIN):
                messages.error(request, 'Access denied. Hospital Administrator credentials required.')
                return redirect('admin_login')

            # Ensure superuser role is synced to ADMIN
            if user.is_superuser and user.role != User.Role.ADMIN:
                user.role = User.Role.ADMIN
                user.save()

            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid administrator username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'portal_title': 'Hospital Administrator Login',
        'portal_subtitle': 'Sign in to manage doctors, approve patients, and oversee hospital records.',
        'is_patient': False,
    })


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('login')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_superuser or user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    elif user.role == User.Role.DOCTOR:
        return redirect('doctor_dashboard')
    elif user.role == User.Role.PATIENT:
        return redirect('patient_dashboard')
    return redirect('login')
