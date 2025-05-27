from django import forms
from django.contrib.auth.models import User
from .models import Client
from django.contrib.auth import get_user_model


from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Client
from django.core.exceptions import ValidationError

User = get_user_model()


class ClientRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"autofocus": False})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Client.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
                date_of_birth=self.cleaned_data["date_of_birth"],
            )
        return user


from django import forms
from .models import Consultant, Service


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Consultant, User


class ConsultantForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    generate_password = forms.BooleanField(
        required=False,
        initial=True,
        label="Generate random password",
        help_text="Uncheck to set a specific password",
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave empty if generating random password",
    )

    class Meta:
        model = Consultant
        fields = ["expertise", "bio", "hourly_rate", "is_active", "photo"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "user" in self.fields:
            del self.fields["user"]

    def clean(self):
        cleaned_data = super().clean()
        generate_password = cleaned_data.get("generate_password")
        password = cleaned_data.get("password")

        if not generate_password and not password:
            raise forms.ValidationError(
                "Please enter a password or check 'Generate random password'"
            )

        return cleaned_data

    def save(self, commit=True):
        # Generate password if needed
        if self.cleaned_data["generate_password"]:
            from django.utils.crypto import get_random_string

            password = get_random_string(12)
        else:
            password = self.cleaned_data["password"]

        # Create the User account
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=password,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        # Add to Consultant group
        from django.contrib.auth.models import Group

        consultant_group, created = Group.objects.get_or_create(name="Consultant")
        user.groups.add(consultant_group)

        # Create the Consultant profile
        consultant = super().save(commit=False)
        consultant.user = user

        if commit:
            consultant.save()
            self.save_m2m()

            # Send welcome email with credentials
            self.send_welcome_email(user, password)

        return consultant

    def send_welcome_email(self, user, password):
        subject = "Your Consultant Account Credentials"
        context = {
            "full_name": user.get_full_name(),
            "email": user.email,
            "password": password,
            "login_url": settings.LOGIN_URL,
        }

        html_message = render_to_string("emails/consultant_welcome.html", context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "consultant"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


from django import forms
from django.utils import timezone
from .models import Appointment
from datetime import datetime, timedelta


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["service", "start_time", "mode"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        consultant = kwargs.pop("consultant")
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = consultant.services.all()

        # Set minimum datetime for the appointment (e.g., at least 1 hour from now)
        min_datetime = timezone.now() + timedelta(hours=1)
        self.fields["start_time"].widget.attrs["min"] = min_datetime.strftime(
            "%Y-%m-%dT%H:%M"
        )


from django import forms
from .models import Consultant


class ConsultantProfileForm(forms.ModelForm):
    class Meta:
        model = Consultant
        fields = ["expertise", "bio", "hourly_rate", "photo", "is_active"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


from django import forms
from .models import Availability


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ["day_of_week", "start_time", "end_time", "is_peak_hour"]
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "end_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "is_peak_hour": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after start time")

        return cleaned_data



# assist/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your full name',
        'required': 'required'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your email address',
        'required': 'required'
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject of your message',
        'required': 'required'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Your message...',
        'rows': 5,
        'required': 'required'
    }))
    consent = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))