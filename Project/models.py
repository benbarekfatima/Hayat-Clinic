from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from datetime import time

class Patient(models.Model):
    pid = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, null=False)
    phone_number = models.CharField(max_length=15, unique=True, null=False, blank=False)
    address = models.CharField(max_length=200, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')


class Doctor(models.Model):
    did = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    SPECIALITY_CHOICES = [
        ("GENERALIST", "Generalist"),
        ("CARDIO", "Cardiologist"),
        ("DERM", "Dermatologist"),
        ("NEURO", "Neurologist"),
        ("ORTHO", "Orthopedic Surgeon"),
        ("ENT", "Otolaryngologist (ENT Specialist)"),
        ("PEDI", "Pediatrician"),
        ("PSYCH", "Psychiatrist"),
    ]
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    address = models.TextField(null=False, blank=False)
    date_recruitment = models.DateField(null=False, blank=False)
    speciality = models.CharField(max_length=10, choices=SPECIALITY_CHOICES, null=False, blank=False)
    def full_name_with_speciality(self):
        return f"{self.user.get_full_name()} ({self.get_speciality_display()})"
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_speciality_display()})"



class Appointment(models.Model):
    aid = models.AutoField(primary_key=True)
    APPOINTMENT_STATES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    TIME_CHOICES = [
        (time(hour, 0), f'{hour}:00')
        for hour in range(9, 12)  # Exclude 12:00
    ] + [
        (time(hour, 0), f'{hour}:00')
        for hour in range(13, 15)  # After lunch, resume from 13:00
    ]
    time_slot = models.TimeField(choices=TIME_CHOICES, default=TIME_CHOICES[0][0], null=False, blank=False)

    full_time = models.DateTimeField(null=False, blank=False)
    state = models.CharField(max_length=20, choices=APPOINTMENT_STATES, null=False, blank=False,default=APPOINTMENT_STATES[0][0])
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='appointments_as_doctor')



class Diagnosis(models.Model):
    condition = models.CharField(max_length=300,null=False, blank=False)
    classification = models.CharField(max_length=300,null=False, blank=False)
    symptoms = models.TextField(null=False, blank=False)
    treatement = models.TextField(null=False, blank=False)
    medica_advice = models.TextField(null=False, blank=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='diagnosis', null=True, blank=True)


class MedicalRecord(models.Model):
    mid = models.AutoField(primary_key=True)
    insurance_provider = models.CharField(max_length=100)
    insurance_policy_number = models.CharField(max_length=50,unique=True)
    insurance_expiry_date = models.DateField(blank=False, null=False)
    family_medical_history = models.TextField(blank=True, null=True)
    past_illnesses = models.TextField(blank=True, null=True)
    surgeries = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    patient = models.OneToOneField('Patient', on_delete=models.CASCADE, related_name='medical_record')



class Task(models.Model):
    tid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateField()
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)





