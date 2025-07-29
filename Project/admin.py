from django.contrib import admin
from .models import Diagnosis, MedicalRecord, Patient, Doctor, Appointment, Task

admin.site.register(Diagnosis)
admin.site.register(MedicalRecord)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Task)