from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DoctorProfile, PatientProfile


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    blood_group = forms.CharField(max_length=5, required=False)
    emergency_contact = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                blood_group=self.cleaned_data['blood_group'],
                emergency_contact=self.cleaned_data['emergency_contact'],
                address=self.cleaned_data['address'],
                is_approved=False  # Requires Admin approval before login
            )
        return user


class AdminAddDoctorForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    specialization = forms.CharField(max_length=100, required=True)
    license_number = forms.CharField(max_length=50, required=True)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                license_number=self.cleaned_data['license_number'],
                consultation_fee=self.cleaned_data['consultation_fee'],
                is_approved=True  # Added directly by Admin
            )
        return user
