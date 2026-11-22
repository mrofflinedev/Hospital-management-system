from django.urls import path
from . import views

urlpatterns = [
    path('register/patient/', views.register_patient, name='register_patient'),
    path('login/', views.login_portal, name='login'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]
