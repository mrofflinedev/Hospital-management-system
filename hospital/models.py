from django.db import models
from django.utils import timezone
from accounts.models import DoctorProfile, PatientProfile


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.TimeField()
    symptoms = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date', '-time_slot']

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date}"


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    diagnosis = models.TextField()
    prescription = models.TextField()
    doctor_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.appointment.patient} ({self.appointment.appointment_date})"


class Bill(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='bill')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    medication_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    mpesa_checkout_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_phone = models.CharField(max_length=15, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.consultation_fee + self.medication_charges
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"Bill #{self.id} - {self.appointment.patient} ({status})"


class Medicine(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100, help_text="e.g., Antibiotic, Painkiller, Antimalarial")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def is_low_stock(self):
        return self.stock_quantity <= 10

    def __str__(self):
        return f"{self.name} (KES {self.unit_price} | Stock: {self.stock_quantity})"


class DispensedMedicine(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='dispensed_medicines')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    dispensed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.medicine.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name} for {self.appointment.patient}"


class LabTest(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (KES {self.cost})"


class LabRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Result'
        COMPLETED = 'COMPLETED', 'Completed'

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='lab_requests')
    test = models.ForeignKey(LabTest, on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    result_notes = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.test.name} for {self.appointment.patient} ({self.get_status_display()})"


class Ward(models.Model):
    class WardType(models.TextChoices):
        GENERAL = 'GENERAL', 'General Ward'
        MATERNITY = 'MATERNITY', 'Maternity Ward'
        PEDIATRIC = 'PEDIATRIC', 'Pediatric Ward'
        PRIVATE = 'PRIVATE', 'Private Room'

    name = models.CharField(max_length=100, unique=True)
    ward_type = models.CharField(max_length=20, choices=WardType.choices, default=WardType.GENERAL)
    total_beds = models.PositiveIntegerField(default=10)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Daily bed charge in KES")

    @property
    def occupied_beds(self):
        return self.admissions.filter(is_discharged=False).count()

    @property
    def available_beds(self):
        return max(0, self.total_beds - self.occupied_beds)

    def __str__(self):
        return f"{self.name} ({self.get_ward_type_display()}) — {self.available_beds}/{self.total_beds} Beds Free (KES {self.daily_rate}/day)"


class Admission(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='admissions')
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name='admissions')
    admitting_doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True)
    bed_number = models.CharField(max_length=20)
    reason = models.TextField()
    admitted_at = models.DateTimeField(default=timezone.now)
    discharged_at = models.DateTimeField(blank=True, null=True)
    is_discharged = models.BooleanField(default=False)

    @property
    def days_admitted(self):
        end_time = self.discharged_at or timezone.now()
        delta = end_time.date() - self.admitted_at.date()
        return max(1, delta.days)

    @property
    def total_ward_cost(self):
        return self.days_admitted * self.ward.daily_rate

    def __str__(self):
        status = "Discharged" if self.is_discharged else f"Bed {self.bed_number}"
        return f"{self.patient} — {self.ward.name} ({status})"
