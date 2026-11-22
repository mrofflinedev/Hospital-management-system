from django import forms
from .models import (
    Appointment,
    MedicalRecord,
    Medicine,
    DispensedMedicine,
    Bill,
    LabTest,
    LabRequest,
)
from accounts.models import DoctorProfile


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'time_slot', 'symptoms')
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'time_slot': forms.TimeInput(attrs={'type': 'time'}),
            'symptoms': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_approved=True)


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ('diagnosis', 'prescription', 'doctor_notes')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 3}),
            'doctor_notes': forms.Textarea(attrs={'rows': 2}),
        }


class AdminInvoiceForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ('consultation_fee', 'medication_charges', 'is_paid')
        help_texts = {
            'medication_charges': 'Includes dispensed pharmacy items, lab tests, and any extra charges.',
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ('name', 'category', 'unit_price', 'stock_quantity', 'expiry_date')
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class DispenseMedicineForm(forms.ModelForm):
    class Meta:
        model = DispensedMedicine
        fields = ('medicine', 'quantity')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medicine'].queryset = Medicine.objects.filter(stock_quantity__gt=0)

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        quantity = cleaned_data.get('quantity')

        if medicine and quantity and quantity > medicine.stock_quantity:
            raise forms.ValidationError(
                f"Only {medicine.stock_quantity} units of {medicine.name} available in stock."
            )
        return cleaned_data


class LabTestCatalogForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ('name', 'description', 'cost')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class LabRequestForm(forms.ModelForm):
    class Meta:
        model = LabRequest
        fields = ('test',)


class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabRequest
        fields = ('result_notes',)
        widgets = {
            'result_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter clinical laboratory findings...'}),
        }
