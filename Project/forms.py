from django import forms
from django.forms import DateInput
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from . import models
from django.forms import ModelChoiceField
from django.utils import timezone
from datetime import timedelta

class UserForm(forms.ModelForm):
    email = forms.EmailField(validators=[validate_email], required=True)
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already in use.')
        return username
    

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = models.MedicalRecord
        fields = [
            'insurance_provider',
            'insurance_policy_number',
            'insurance_expiry_date',
            'family_medical_history',
            'past_illnesses',
            'surgeries',
            'allergies',
        ]
        widgets = {
        'insurance_expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PatientForm(forms.ModelForm):
    phone_number_regex = re.compile(r'^0[5-7]\d{8}$')
    emergency_contact_regex = re.compile(r'^0[5-7]\d{8}$')

    phone_number = forms.RegexField(
        phone_number_regex, max_length=15, required=True,
        help_text='Enter your phone number (10 digits).',
        error_messages={'invalid': 'Enter a valid phone number (10 digits).'}
    )
    address = forms.CharField(required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    emergency_contact = forms.RegexField(
        emergency_contact_regex, max_length=15, required=True,
        help_text='Enter your emergency contact number (10 digits).',
        error_messages={'invalid': 'Enter a valid emergency contact number (10 digits).'}
    )
    gender = forms.ChoiceField(
        choices=models.Patient.GENDER_CHOICES, required=True, widget=forms.Select()
    )

    class Meta:
        model = models.Patient
        fields = ['phone_number', 'address', 'date_of_birth', 'emergency_contact', 'gender']





class DoctorForm(forms.ModelForm):
    phone_number_regex = re.compile(r'^0[5-7]\d{8}$')
    phone_number = forms.RegexField(
        phone_number_regex, max_length=15, required=True,
        help_text='Enter your phone number (10 digits).',
        error_messages={'invalid': 'Enter a valid phone number (10 digits).'}
    )
    address = forms.CharField(required=True)
    date_recruitment = forms.DateField(required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    speciality = forms.ChoiceField(
        choices=models.Doctor.SPECIALITY_CHOICES, required=True, widget=forms.Select()
    )

    class Meta:
        model = models.Doctor
        fields = ['phone_number', 'address', 'date_recruitment', 'speciality']



class UserLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())



class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        label='Doctor',
        queryset=models.Doctor.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='did',  # Use 'did' as the value for the doctor field
        empty_label='Select Doctor',
    )

    # Override the __init__ method to dynamically set choices for full_time
    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)

        # Generate choices for the next 10 days starting from tomorrow
        tomorrow = timezone.now() + timedelta(days=1)
        upcoming_dates = [tomorrow + timedelta(days=i) for i in range(10)]
        date_choices = [(date, date.strftime('%Y-%m-%d')) for date in upcoming_dates]

        self.fields['full_time'].widget = forms.Select(choices=date_choices)
        self.fields['full_time'].label = 'Select Date'

    class Meta:
        model = models.Appointment
        fields = ['doctor', 'full_time', 'time_slot']
        widgets = {
            'time_slot': forms.Select(choices=models.Appointment.TIME_CHOICES),
        }

class RescheduleAppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generate choices for the next 10 days starting from tomorrow
        tomorrow = timezone.now() + timedelta(days=1)
        upcoming_dates = [tomorrow + timedelta(days=i) for i in range(10)]
        date_choices = [(date, date.strftime('%Y-%m-%d')) for date in upcoming_dates]

        # Update choices for 'full_time'
        self.fields['full_time'].widget = forms.Select(choices=date_choices)
        self.fields['full_time'].label = 'Select Date'

    class Meta:
        model = models.Appointment
        fields = ['full_time', 'time_slot']
        widgets = {
            'time_slot': forms.Select(choices=models.Appointment.TIME_CHOICES),
        }


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = models.Diagnosis
        fields = [
            'condition',
            'classification',
            'symptoms',
            'treatement',
            'medica_advice',
        ]
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['title', 'description', 'deadline', 'assigned_doctor']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }