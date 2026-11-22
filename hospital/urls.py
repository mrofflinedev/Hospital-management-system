from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book/', views.book_appointment, name='book_appointment'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointment/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('doctor/consult/<int:appointment_id>/', views.complete_consultation, name='complete_consultation'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add-doctor/', views.admin_add_doctor, name='admin_add_doctor'),
    path('admin-panel/approve-patient/<int:patient_id>/', views.approve_patient, name='approve_patient'),
    path('admin-panel/pay-bill/<int:bill_id>/', views.mark_bill_paid, name='mark_bill_paid'),
    # Pharmacy & Inventory
    path('pharmacy/inventory/', views.pharmacy_inventory, name='pharmacy_inventory'),
    path('pharmacy/restock/<int:medicine_id>/', views.restock_medicine, name='restock_medicine'),
    path('pharmacy/dispense/<int:appointment_id>/', views.dispense_medicine, name='dispense_medicine'),
    # Printable Invoices
    path('invoice/<int:bill_id>/', views.print_invoice, name='print_invoice'),
    path('admin-panel/create-invoice/', views.admin_create_invoice, name='admin_create_invoice_select'),
    path('admin-panel/create-invoice/<int:appointment_id>/', views.admin_create_invoice, name='admin_create_invoice'),
    # Laboratory Diagnostics
    path('laboratory/catalog/', views.lab_catalog, name='lab_catalog'),
    path('laboratory/appointment/<int:appointment_id>/', views.manage_appointment_labs, name='manage_appointment_labs'),

]
