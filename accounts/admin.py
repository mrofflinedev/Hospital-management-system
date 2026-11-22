from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, PatientProfile


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact Info', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Contact Info', {'fields': ('role', 'phone_number')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')


admin.site.register(User, CustomUserAdmin)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
