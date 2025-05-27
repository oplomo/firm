from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

User = get_user_model()


class Client(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    referral_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()


class Consultant(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="consultant_profile"
    )
    expertise = models.CharField(max_length=255)
    bio = models.TextField()
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="consultant/", null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    consultant = models.ForeignKey(
        Consultant, on_delete=models.CASCADE, related_name="services"
    )

    def __str__(self):
        return f"{self.name} ({self.consultant})"


class Availability(models.Model):
    consultant = models.ForeignKey(
        Consultant, on_delete=models.CASCADE, related_name="availabilities"
    )
    day_of_week = models.CharField(
        max_length=9,
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ],
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_peak_hour = models.BooleanField(default=False)  # for analytics, optional

    def __str__(self):
        return f"{self.consultant} - {self.day_of_week} ({self.start_time}-{self.end_time})"

    @property
    def duration_hours(self):
        start = datetime.datetime.combine(datetime.date.today(), self.start_time)
        end = datetime.datetime.combine(datetime.date.today(), self.end_time)
        duration = end - start
        return round(duration.total_seconds() / 3600, 1)


class Appointment(models.Model):
    MODE_CHOICES = (
        ("virtual", "Virtual Consultation"),
        ("physical", "Physical Meeting"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )
    meet_link = models.URLField(blank=True, null=True)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="appointments"
    )
    consultant = models.ForeignKey(
        Consultant, on_delete=models.CASCADE, related_name="appointments"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} with {self.consultant} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def is_upcoming(self):
        return self.start_time > timezone.now()

    def duration(self):
        return (self.end_time - self.start_time).seconds // 60  # in minutes


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("mpesa", "M-Pesa Paybill"),
        ("bank_transfer", "Bank Transfer"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending Verification"),
        ("confirmed", "Confirmed"),
        ("rejected", "Rejected"),
    )

    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_date = models.DateTimeField(auto_now_add=True)
    verified_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for {self.appointment}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user.username}"


class MpesaTransaction(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    transaction_id = models.CharField(max_length=50, unique=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="mpesa_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_date = models.DateTimeField(auto_now_add=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    response_code = models.CharField(max_length=10, blank=True, null=True)
    response_description = models.TextField(blank=True, null=True)
    result_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} ({self.status})"
