from django.contrib import admin
from .models import Appointment, MedicalRecord, Bill, Medicine, DispensedMedicine
from .models import Appointment, MedicalRecord, Bill, Medicine, DispensedMedicine, LabTest, LabRequest

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'time_slot', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__user__username', 'doctor__user__username')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'created_at')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'total_amount', 'is_paid', 'generated_at')
    list_filter = ('is_paid',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_price', 'stock_quantity', 'expiry_date')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(DispensedMedicine)
class DispensedMedicineAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'medicine', 'quantity', 'subtotal', 'dispensed_at')
@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ('name',)


@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'test', 'status', 'requested_at')
    list_filter = ('status',)

from .models import Ward, Admission


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward_type', 'total_beds', 'occupied_beds', 'available_beds', 'daily_rate')


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'ward', 'bed_number', 'admitted_at', 'is_discharged')
    list_filter = ('is_discharged', 'ward')
