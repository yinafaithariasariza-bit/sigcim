from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Appointment, Patient, Doctor, MedicalRecord


class StyledMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input',
                'autocomplete': 'off',
            })


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class AppointmentForm(StyledMixin, forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'scheduled_at', 'duration_minutes', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields['scheduled_at'].widget.attrs['class'] = 'form-input'
        self.fields['reason'].widget.attrs['class'] = 'form-input'

    def clean_scheduled_at(self):
        dt = self.cleaned_data['scheduled_at']
        if dt < timezone.now():
            raise forms.ValidationError("Appointment must be scheduled in the future.")
        return dt


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


class MedicalRecordForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'prescription', 'follow_up_date']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'treatment': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'prescription': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
