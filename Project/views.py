from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from .forms import (
    UserForm, PatientForm, DoctorForm, UserLoginForm,
    MedicalRecordForm, AppointmentForm, RescheduleAppointmentForm, DiagnosisForm,TaskForm
)
from .models import Patient, Doctor, Appointment, Diagnosis, MedicalRecord,Task


def home(request):
    return render(request, 'home.html')

def signUpPatient(request):
    if request.method == 'POST':
        userForm = UserForm(request.POST)
        patientForm = PatientForm(request.POST)
        medicalRecordForm = MedicalRecordForm(request.POST)

        if userForm.is_valid() and patientForm.is_valid() and medicalRecordForm.is_valid():
            user = User.objects.create_user(
                username=userForm.cleaned_data['username'],
                password=userForm.cleaned_data['password'],
                email=userForm.cleaned_data['email'],
                first_name=userForm.cleaned_data['first_name'],
                last_name=userForm.cleaned_data['last_name']
            )
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.save()

            medical_record = medicalRecordForm.save(commit=False)
            medical_record.patient = patient
            medical_record.save()

            my_patient_group, _ = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)

            login(request, user)

            subject='Welcome to Hayat Clinic'
            message=f"Dear {patient.user.get_full_name()}n\n"\
                        "you have been successefully signed up to hayat clinic!\n\n"\
                        "Thank you for choosing Hayat Clinic\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"    
            from_email='hayatclinic89@gmail.com'
            recipient_list=[user.email]
            send_mail(subject, message, from_email, recipient_list)

            return HttpResponseRedirect('/project/appointements_pat')

    else:
        userForm = UserForm()
        patientForm = PatientForm()
        medicalRecordForm = MedicalRecordForm()

    return render(request, 'patientsignup.html', context={'userForm': userForm, 'patientForm': patientForm, 'medicalRecordForm': medicalRecordForm})

def signUpDoctor(request):
    if request.method == 'POST':
        userForm = UserForm(request.POST)
        doctorForm = DoctorForm(request.POST)
        if userForm.is_valid() and doctorForm.is_valid():
            user = User.objects.create_user(
                username=userForm.cleaned_data['username'],
                password=userForm.cleaned_data['password'],
                email=userForm.cleaned_data['email'],
                first_name=userForm.cleaned_data['first_name'],
                last_name=userForm.cleaned_data['last_name']
            )
            doctor = doctorForm.save(commit=False)
            doctor.user = user
            doctor.save()

            my_doctor_group, _ = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group.user_set.add(user)

            subject='Welcome to Hayat Clinic'
            message=f"Dear {user.get_full_name()},\n\n"\
                        "you have been successefully signed up to hayat clinic!\n\n"\
                        "Thank you for choosing Hayat Clinic\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team" 
            from_email='hayatclinic89@gmail.com'
            recipient_list=[user.email]
            send_mail(subject, message, from_email, recipient_list)

            return redirect('admin_doctors')  # Redirect to the admin doctors page after successful signup
    else:
        userForm = UserForm()
        doctorForm = DoctorForm()
    return render(request, 'doctorsignup.html', context={'userForm': userForm, 'doctorForm': doctorForm})

def user_login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name='PATIENT').exists():
                    return HttpResponseRedirect('/project/appointements_pat')
                elif user.groups.filter(name='DOCTOR').exists():
                    return HttpResponseRedirect('/project/appointements_doc')
                elif user.is_staff:
                    return HttpResponseRedirect('/project/admin/home/')  # Redirect to the admin home
    else:
        login_form = UserLoginForm()

    return render(request, 'login.html', {'login_form': login_form})

def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def appointements_pat(request):
    user = request.user
    patient = Patient.objects.get(user=user)
    appointments = Appointment.objects.filter(patient=patient, state='scheduled')
    doctors = Doctor.objects.all()

    return render(request, 'appointements_patient.html', {'user': user, 'appointments': appointments, 'doctors': doctors})

@login_required
def schedule_appointment_pat(request):
    form = AppointmentForm()
    messages = []

    doctors_with_speciality = [
        (doctor.did, doctor.full_name_with_speciality())
        for doctor in Doctor.objects.all()
    ]
    form.fields['doctor'].choices = doctors_with_speciality

    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            doctor_id = form.cleaned_data['doctor'].did
            date = form.cleaned_data['full_time']
            time_slot = form.cleaned_data['time_slot']

            try:
                doctor = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist:
                messages.append('Selected doctor not found.')
                form.errors.clear()
                return render(request, 'schedule_appointement_pat.html', {'form': form, 'messages': messages})

            datetime_obj = datetime.combine(date, time_slot)
            patient = request.user.patient

            if not is_time_slot_available(patient,doctor,datetime_obj):
                messages.append('Selected time slot is not available.')
                form.errors.clear()
                return render(request, 'schedule_appointement_pat.html', {'form': form, 'messages': messages})

            appointment = form.save(commit=False)
            appointment.patient = request.user.patient
            appointment.doctor = doctor
            appointment.full_time = datetime_obj
            appointment.save()

            messages.append('Appointment successfully scheduled!')

            subject='Appointment successfully scheduled'
            message_pat =f"We are pleased to inform you that your appointment has been successfully scheduled.\n"\
                        f"You are scheduled to meet with Dr. {doctor.full_name_with_speciality()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Thank you for choosing Hayat Clinic. We look forward to seeing you!\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"   
            message_doc =f"We are pleased to inform you that your appointment has been successfully scheduled.\n"\
                        f"You are scheduled to meet with {patient.user.get_full_name()}  on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"          
            from_email='hayatclinic89@gmail.com'
            send_mail(subject, message_pat, from_email,[patient.user.email])
            send_mail(subject, message_doc, from_email,[doctor.user.email])

            return redirect('appointements_pat')

    return render(request, 'schedule_appointement_pat.html', {'form': form, 'messages': messages})

def is_time_slot_available(patient, doctor, datetime_obj):
    existing_patient_appointments = Appointment.objects.filter(
        patient=patient,
        full_time=datetime_obj,
        state='scheduled'
    )

    existing_doctor_appointments = Appointment.objects.filter(
        doctor=doctor,
        full_time=datetime_obj,
        state='scheduled'
    )

    # Check if there are no scheduled appointments for both patient and doctor
    return not (existing_patient_appointments.exists() or existing_doctor_appointments.exists())


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)

    if appointment.patient == request.user.patient:
        appointment.state = 'canceled'
        appointment.save()
        subject='Appointment canceled'
        message_pat = f"Dear {request.user.first_name} {request.user.last_name},\n\n"\
                        f"We inform you that your appointment has been canceled.\n"\
                        f"You were scheduled to meet with Dr. {appointment.doctor.full_name_with_speciality()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"
        message_doc = f"Dear {appointment.doctor.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been canceled.\n"\
                        f"You were scheduled to meet with {request.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"           
        from_email='hayatclinic89@gmail.com'
        send_mail(subject, message_pat, from_email, [request.user.email])
        send_mail(subject, message_doc, from_email, [appointment.doctor.user.email])

        return redirect('appointements_pat')
    else:
        return render(request, 'error_page.html', {'message': 'Appointment not found or unauthorized'})



def delete_appointment_doc(request, appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)

    if appointment.doctor == request.user.doctor:
        appointment.state = 'canceled'
        appointment.save()
        subject='Appointment canceled'
        message_pat =  f"Dear {appointment.patient.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been canceled.\n"\
                        f"You were scheduled to meet with Dr. {appointment.doctor.full_name_with_speciality()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"
        message_doc = f"Dear {request.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been canceled.\n"\
                        f"You were scheduled to meet with {appointment.patient.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"           
        from_email='hayatclinic89@gmail.com'
        send_mail(subject, message_pat, from_email, [appointment.patient.user.email])
        send_mail(subject, message_doc, from_email, [request.user.email])
        return redirect('appointements_doc')
    else:
        return render(request, 'error_page.html', {'message': 'Appointment not found or unauthorized'})


def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)
    messages = []
    if appointment.patient == request.user.patient:
        if request.method == 'POST':
            form = RescheduleAppointmentForm(request.POST, instance=appointment)
            if form.is_valid():
                new_date = form.cleaned_data['full_time'].date()
                new_time_slot = form.cleaned_data['time_slot']

                datetime_obj = datetime.combine(new_date, new_time_slot)
                patient = request.user.patient

                if not is_time_slot_available(patient,appointment.doctor,datetime_obj):
                    messages.append('Selected time slot is not available.')
                    form.errors.clear()
                    return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment, 'messages': messages})

                # Update the full_time and time_slot fields
                appointment.full_time = datetime.combine(new_date, new_time_slot)
                appointment.save()

                subject='Appointment rescheduled'
                message_pat =f"Dear {request.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been rescheduled.\n"\
                        f"You are scheduled to meet with Dr.{appointment.doctor.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
                message_doc =f"Dear {appointment.doctor.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been rescheduled.\n"\
                        f"You are scheduled to meet with {appointment.patient.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
                from_email='hayatclinic89@gmail.com'
                send_mail(subject, message_pat, from_email, [request.user.email])
                send_mail(subject, message_doc, from_email, [appointment.doctor.user.email])

                return HttpResponseRedirect(reverse('appointements_pat'))
        else:
            form = RescheduleAppointmentForm(instance=appointment)

        return render(request, 'reschedule_appointment.html', {'form': form, 'appointment': appointment, 'messages': messages})
    else:
        return render(request, 'error_page.html', {'message': 'Appointment not found or unauthorized'})


def reschedule_appointment_doc(request, appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)
    messages = []
    if appointment.doctor == request.user.doctor:
        if request.method == 'POST':
            form = RescheduleAppointmentForm(request.POST, instance=appointment)
            if form.is_valid():
                new_date = form.cleaned_data['full_time'].date()
                new_time_slot = form.cleaned_data['time_slot']

                # Check if the new time slot is available
                
                datetime_obj = datetime.combine(new_date, new_time_slot)
                patient = appointment.patient

                if not is_time_slot_available(patient,appointment.doctor,datetime_obj):
                    messages.append('Selected time slot is not available.')
                    form.errors.clear()
                    return render(request, 'reschedule_appointment.html', {'form': form,'doctor':appointment.doctor, 'appointment': appointment, 'messages': messages})

                # Update the full_time and time_slot fields
                appointment.full_time = datetime.combine(new_date, new_time_slot)
                appointment.save()

                subject='Appointment rescheduled'
                message_doc =f"Dear {request.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been rescheduled.\n"\
                        f"You are scheduled to meet with {appointment.patient.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
                message_pat =f"Dear {appointment.patient.user.get_full_name()},\n\n"\
                        f"We inform you that your appointment has been rescheduled.\n"\
                        f"You are scheduled to meet with Dr.{appointment.doctor.user.get_full_name()} on "\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
                from_email='hayatclinic89@gmail.com'
                send_mail(subject, message_doc, from_email, [request.user.email])
                send_mail(subject, message_pat, from_email,[appointment.patient.user.email])
          
                return HttpResponseRedirect(reverse('appointements_doc'))
        else:
            form = RescheduleAppointmentForm(instance=appointment)

        return render(request, 'reschedule_appointment.html', {'form': form, 'doctor':appointment.doctor, 'appointment': appointment, 'messages': messages})
    else:
        return render(request, 'error_page.html', {'message': 'Appointment not found or unauthorized'})


def fill_diagnosis(request, appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)
    messages = []
    if appointment.doctor == request.user.doctor:
        if request.method=="POST":
            form = DiagnosisForm(request.POST)
            if form.is_valid():
                condition = form.cleaned_data['condition']
                classification = form.cleaned_data['classification']
                symptoms = form.cleaned_data['symptoms']
                treatement = form.cleaned_data['treatement']
                medica_advice = form.cleaned_data['medica_advice']
                diagnosis_appointment = appointment
                diagnosis = Diagnosis()
                diagnosis.condition = condition
                diagnosis.classification = classification
                diagnosis.symptoms = symptoms
                diagnosis.treatement = treatement
                diagnosis.medica_advice = medica_advice
                diagnosis.appointment = diagnosis_appointment
                diagnosis.save()
                appointment.state  = "completed"
                appointment.save()
                return HttpResponseRedirect(reverse('appointements_doc'))
        else:
            form = DiagnosisForm(instance=appointment)
            return render(request, 'diagnosis.html', {'form': form, 'appointment': appointment, 'messages': messages})
    else:
        return render(request, 'error_page.html', {'message': 'Appointment not found or unauthorized'})
        

@login_required
def patient_profile(request):
    user = request.user
    patient = Patient.objects.get(user=user)
    medical_record = MedicalRecord.objects.get(patient=patient)

    appointments = Appointment.objects.filter(patient=patient, state='completed')
    diagnoses = Diagnosis.objects.filter(appointment__in=appointments)

    context = {
        'user': user,
        'patient': patient,
        'medical_record': medical_record,
        'diagnoses': diagnoses,
        'appointments': appointments, 
    }

    return render(request, 'patient_profile.html', context)


def doctor_profile(request):
    user = request.user
    doctor =Doctor.objects.get(user=user)

    appointments = Appointment.objects.filter(doctor=doctor, state='completed')
    diagnoses = Diagnosis.objects.filter(appointment__in=appointments)

    context = {
        'user': user,
        'doctor': doctor,
        'diagnoses': diagnoses,
        'appointments': appointments, 
    }

    return render(request, 'doctor_profile.html', context)

def patient_profile_doc(request,appointment_id):
    appointment = get_object_or_404(Appointment, aid=appointment_id)
    patient = appointment.patient
    medical_record = MedicalRecord.objects.get(patient=patient)

    appointments = Appointment.objects.filter(patient=patient)
    diagnoses = Diagnosis.objects.filter(appointment__in=appointments)

    context = {
        'doctor':appointment.doctor,
        'user': patient.user,
        'patient': patient,
        'medical_record': medical_record,
        'diagnoses': diagnoses,
        'appointments': appointments, 
    }

    return render(request, 'patient_profile.html', context)



@login_required
def appointements_doc(request):
    user = request.user
    appointments = []
    if Doctor.objects.filter(user=user).exists():
        appointments = Appointment.objects.filter(doctor__user=user, state='scheduled')
    return render(request, 'appointements_doctor.html', {'user': user, 'appointments': appointments})

@login_required
def doctor_tasks(request):
    # Retrieve tasks for the logged-in doctor
    tasks = Task.objects.filter(assigned_doctor=request.user.doctor)
    return render(request, 'doctor_tasks.html', {'tasks': tasks})


#**************admin views******************

@staff_member_required
@login_required
def admin_home(request):
    return render(request, 'admin_home.html')

@staff_member_required
@login_required
def admin_patients(request):
    patients = Patient.objects.all()
    total_patients = patients.count()

    context = {
        'patients': patients,
        'total_patients': total_patients,
    }

    return render(request, 'admin_patients.html', context)

@staff_member_required
@login_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, pid=patient_id)
    user = patient.user
    patient.delete()
    user.delete()  # Delete associated user

    subject='Account deleted'
    message =f"Dear {user.get_full_name()},\n\n"\
                        f"We inform you that your account has beeen deleted from our clinic database.\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
    from_email='hayatclinic89@gmail.com'
    recipient_list=[user.email]
    send_mail(subject, message, from_email, recipient_list)
    
    return redirect('admin_patients')

@staff_member_required
@login_required
def patient_profile_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    patient = get_object_or_404(Patient, user=user)
    context = {
        'user': user,
        'patient': patient,
    }

    return render(request, 'patient_profile_admin.html', context)

@staff_member_required
@login_required
def admin_doctors(request):
    doctors = Doctor.objects.all()
    total_doctors = doctors.count()
    context = {'doctors': doctors, 'total_doctors': total_doctors}
    return render(request, 'admin_doctors.html', context)

@staff_member_required
@login_required
def doctor_profile_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    doctor = get_object_or_404(Doctor, user=user)
    context = {
        'user': user,
        'doctor': doctor,
    }
    return render(request, 'doctor_profile_admin.html', context)

@staff_member_required
@login_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, did=doctor_id)
    user = doctor.user
    doctor.delete()

    subject='Account deleted'
    message =f"Dear {user.get_full_name()},\n\n"\
                        f"We inform you that your account has beeen deleted from our clinic database.\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
    from_email='hayatclinic89@gmail.com'
    recipient_list=[user.email]
    send_mail(subject, message, from_email, recipient_list)

    user.delete()
    
    return redirect('admin_doctors')

@staff_member_required
@login_required
def admin_appointments(request):
    total_appointments = Appointment.objects.count()
    # Retrieve a list of all appointments with patient and doctor details
    appointments = Appointment.objects.all()
    context = {
        'total_appointments': total_appointments,
        'appointments': appointments,
    }

    return render(request, 'admin_appointments.html', context)

@staff_member_required
@login_required
def delete_appointment_admin(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, aid=appointment_id)
        appointment.state = 'canceled'
        appointment.save()
        subject='Appointment canceled'
        message =f"We inform you that your appointment on"\
                        f"{appointment.full_time.strftime('%A, %B %d, %Y at %I:%M %p')} has been canceled.\n\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
        from_email='hayatclinic89@gmail.com'
        recipient_list=[appointment.patient.user.email,appointment.doctor.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return redirect('admin_appointments')
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        # Handle the error or print more details for debugging
        return render(request, 'error_page.html', {'message': 'Error deleting appointment'})


@staff_member_required
@login_required
def admin_tasks(request):
    tasks = Task.objects.all()  # Retrieve all tasks from the database
    return render(request, 'admin_tasks.html', {'tasks': tasks})

@staff_member_required
@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_doctor_id = request.POST['assigned_doctor']
            task.save()
            subject='Task added'
            message =f"We inform you that you have a new task.\n"\
                        "Best regards,\n"\
                        "Hayat Clinic Team"  
            from_email='hayatclinic89@gmail.com'
            recipient_list=[task.assigned_doctor.user.email]
            send_mail(subject, message, from_email, recipient_list)
            return redirect('admin_tasks')
        else:
            print(form.errors)  
    else:
        form = TaskForm()

    return render(request, 'add_task.html', {'form': form})

@staff_member_required
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, tid=task_id)
    task.delete()
    
    return redirect('admin_tasks')


