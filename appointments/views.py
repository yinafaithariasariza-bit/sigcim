from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Appointment, Patient, Doctor, MedicalRecord
from .forms import AppointmentForm, AppointmentStatusForm, MedicalRecordForm, LoginForm


class SIGCIMLoginView(LoginView):
    template_name = 'appointments/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SIGCIMLogoutView(LogoutView):
    next_page = '/login/'


@login_required
def dashboard(request):
    today = timezone.now().date()
    upcoming = Appointment.objects.filter(
        scheduled_at__date=today,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
    ).select_related('patient__user', 'doctor__user', 'doctor__specialty').order_by('scheduled_at')

    stats = {
        'today_count': upcoming.count(),
        'pending': Appointment.objects.filter(status=Appointment.STATUS_PENDING).count(),
        'confirmed': Appointment.objects.filter(status=Appointment.STATUS_CONFIRMED).count(),
        'total_patients': Patient.objects.count(),
    }

    recent = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).order_by('-created_at')[:5]

    return render(request, 'appointments/dashboard.html', {
        'upcoming': upcoming,
        'stats': stats,
        'recent': recent,
    })


@login_required
def appointment_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    qs = Appointment.objects.select_related(
        'patient__user', 'doctor__user', 'doctor__specialty'
    ).order_by('-scheduled_at')

    if status_filter:
        qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(
            Q(patient__user__first_name__icontains=search) |
            Q(patient__user__last_name__icontains=search) |
            Q(doctor__user__last_name__icontains=search)
        )

    return render(request, 'appointments/appointment_list.html', {
        'appointments': qs,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.created_by = request.user
        appointment.save()
        messages.success(request, "Appointment scheduled successfully.")
        return redirect('appointment_detail', pk=appointment.pk)
    return render(request, 'appointments/appointment_form.html', {'form': form, 'action': 'Create'})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__specialty', 'created_by'
        ),
        pk=pk
    )
    status_form = AppointmentStatusForm(instance=appointment)
    record_form = None
    medical_record = getattr(appointment, 'medical_record', None)

    if appointment.status == Appointment.STATUS_COMPLETED and not medical_record:
        record_form = MedicalRecordForm()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            status_form = AppointmentStatusForm(request.POST, instance=appointment)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Status updated.")
                return redirect('appointment_detail', pk=pk)

        elif 'save_record' in request.POST:
            record_form = MedicalRecordForm(request.POST)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.appointment = appointment
                record.save()
                messages.success(request, "Medical record saved.")
                return redirect('appointment_detail', pk=pk)

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'status_form': status_form,
        'record_form': record_form,
        'medical_record': medical_record,
    })


@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not appointment.can_be_cancelled():
        messages.error(request, "This appointment cannot be cancelled.")
        return redirect('appointment_detail', pk=pk)
    if request.method == 'POST':
        appointment.status = Appointment.STATUS_CANCELLED
        appointment.save()
        messages.success(request, "Appointment cancelled.")
        return redirect('appointment_list')
    return render(request, 'appointments/appointment_confirm_cancel.html', {'appointment': appointment})


@login_required
def patient_list(request):
    search = request.GET.get('q', '')
    qs = Patient.objects.select_related('user').order_by('user__last_name')
    if search:
        qs = qs.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    return render(request, 'appointments/patient_list.html', {'patients': qs, 'search': search})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient.objects.select_related('user'), pk=pk)
    appointments = patient.appointments.select_related(
        'doctor__user', 'doctor__specialty'
    ).order_by('-scheduled_at')
    return render(request, 'appointments/patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
    })


@login_required
def doctor_list(request):
    doctors = Doctor.objects.select_related('user', 'specialty').filter(is_available=True)
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})
