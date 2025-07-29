from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/home/', views.admin_home, name='admin_home'),
    path('admin/patients/', views.admin_patients, name='admin_patients'),
    path('admin/patients/<int:user_id>/', views.patient_profile_admin, name='patient_profile_admin'),
    path('admin/patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('admin/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin/doctors/<int:user_id>/', views.doctor_profile_admin, name='doctor_profile_admin'),
    path('admin/doctors/delete/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('admin/doctors/signUpDoctor/',views.signUpDoctor,name='sign_up_doctor'),
    path('admin/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin/appointments/delete/<int:appointment_id>/', views.delete_appointment_admin, name='delete_appointment_admin'),
    path('admin/tasks/', views.admin_tasks, name='admin_tasks'),
    path('admin/tasks/add_task', views.add_task, name='add_task'),
    path('admin/tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),

    path('home/',views.home,name='home'),
    path('signUpPatient/',views.signUpPatient,name='sign_up_patient'),
    path('login/', views.user_login, name='login'),
    path('appointements_pat/',views.appointements_pat,name='appointements_pat'),
    path('appointements_doc/',views.appointements_doc,name='appointements_doc'),
    path('logout/', views.user_logout, name='logout'),
    path('schedule-appointment_pat/', views.schedule_appointment_pat, name='schedule_appointment_pat'),
    path('delete_appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment_pat'),
    path('delete_appointment_doc/<int:appointment_id>/', views.delete_appointment_doc, name='delete_appointment_doc'),
    path('reschedule_appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('reschedule_appointment_doc/<int:appointment_id>/', views.reschedule_appointment_doc, name='reschedule_appointment_doc'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('patient_profile_doc/<int:appointment_id>/', views.patient_profile_doc, name='patient_profile_doc'),
    path('fill_diagnosis/<int:appointment_id>/', views.fill_diagnosis, name='fill_diagnosis'),

    path('doctor_tasks/', views.doctor_tasks, name='doctor_tasks'),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

