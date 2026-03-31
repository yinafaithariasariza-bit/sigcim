from django.contrib import admin
from .models import Specialty, Doctor, Patient, Schedule, Appointment, MedicalRecord


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialty', 'license_number', 'is_available']
    list_filter = ['specialty', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'date_of_birth', 'blood_type', 'insurance_number']
    search_fields = ['user__first_name', 'user__last_name', 'insurance_number']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_of_week_display', 'start_time', 'end_time']
    list_filter = ['day_of_week', 'doctor']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'scheduled_at', 'status', 'created_at']
    list_filter = ['status', 'doctor__specialty']
    search_fields = ['patient__user__last_name', 'doctor__user__last_name']
    date_hierarchy = 'scheduled_at'
    readonly_fields = ['created_at', 'updated_at', 'created_by']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'follow_up_date', 'created_at']
    readonly_fields = ['created_at']
