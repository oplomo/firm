from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ClientRegisterForm
from .models import Client
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.core.paginator import Paginator


from django.shortcuts import render
from .models import Consultant, Service


def home(request):
    featured_consultants = Consultant.objects.filter(is_active=True)[:4]  # Get top 4
    services = Service.objects.all()

    context = {
        "featured_consultants": featured_consultants,
        "services": services,
        # Add other data as needed
    }

    return render(request, "assist/home.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import ClientRegisterForm


def register_client(request):
    if request.method == "POST":
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome.")
            return redirect("home")  # Change to your desired redirect
        else:
            # Add form errors to messages for better visibility
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClientRegisterForm()

    return render(request, "registration/register.html", {"form": form})


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def services(request):
    return render(request, "assist/services.html")


from django.db.models import Q


def consultants(request):
    consultants = Consultant.objects.select_related("user").filter(is_active=True)

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        consultants = consultants.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(expertise__icontains=search_query)
            | Q(bio__icontains=search_query)
            | Q(services__name__icontains=search_query)
            | Q(services__description__icontains=search_query)
        ).distinct()

    # Sorting functionality
    sort_by = request.GET.get("sort", "")
    if sort_by == "name":
        consultants = consultants.order_by("user__last_name", "user__first_name")
    elif sort_by == "rate_low":
        consultants = consultants.order_by("hourly_rate")
    elif sort_by == "rate_high":
        consultants = consultants.order_by("-hourly_rate")

    # Filtering by expertise
    selected_expertise = request.GET.get("expertise", "")
    if selected_expertise:
        consultants = consultants.filter(expertise__icontains=selected_expertise)

    # Filtering by service
    selected_service = request.GET.get("service", "")
    if selected_service:
        consultants = consultants.filter(services__name__icontains=selected_service)

    # Pagination
    paginator = Paginator(consultants, 8)  # Show 8 consultants per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get unique expertise for filter dropdown
    expertise_list = (
        Consultant.objects.filter(is_active=True)
        .values_list("expertise", flat=True)
        .distinct()
    )

    # Get unique services for filter dropdown
    service_list = Service.objects.values_list("name", flat=True).distinct()

    context = {
        "consultants": page_obj,
        "search_query": search_query,
        "sort_by": sort_by,
        "selected_expertise": selected_expertise,
        "selected_service": selected_service,
        "expertise_list": expertise_list,
        "service_list": service_list,
    }

    return render(request, "assist/consultants.html", context)


# assist/views.py
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get cleaned data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            # Prepare email content
            email_subject = f"New Contact Form Submission: {subject}"
            email_message = f"""
            You have received a new message from your website contact form.
            
            Name: {name}
            Email: {email}
            Subject: {subject}
            Message:
            {message}
            """

            try:
                # Send email
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Sending to yourself
                    fail_silently=False,
                )

                # Send confirmation to user
                user_subject = "Thank you for contacting us"
                user_message = f"""
                Dear {name},
                
                Thank you for reaching out to us. We have received your message and will get back to you shortly.
                
                Here's a copy of your message:
                Subject: {subject}
                Message: {message}
                
                Best regards,
                ClimbUp Solutions Team
                """

                send_mail(
                    user_subject,
                    user_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],  # Sending to the user
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Your message has been sent successfully! We'll get back to you soon.",
                )
                return redirect("contact")

            except Exception as e:
                messages.error(
                    request,
                    f"Sorry, there was an error sending your message. Please try again later. Error: {str(e)}",
                )
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ContactForm()

    return render(request, "assist/contact.html", {"form": form})


# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your profile has been updated!')
#             return redirect('profile')
#     else:
#         form = ProfileForm(instance=request.user)
#     return render(request, 'assist/profile.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Consultant, Client, Appointment, Service, Payment, Notification
from .forms import ConsultantForm, ServiceForm
from django.utils import timezone


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    # Dashboard statistics
    total_consultants = Consultant.objects.count()
    total_clients = Client.objects.count()
    upcoming_appointments = Appointment.objects.filter(
        start_time__gte=timezone.now()
    ).order_by("start_time")[:5]
    pending_payments = Payment.objects.filter(status="pending").count()

    context = {
        "total_consultants": total_consultants,
        "total_clients": total_clients,
        "upcoming_appointments": upcoming_appointments,
        "pending_payments": pending_payments,
    }
    return render(request, "admin_dashboard/dashboard.html", context)


@user_passes_test(is_admin)
def manage_consultants(request):
    consultants = Consultant.objects.all().select_related("user")
    return render(
        request, "admin_dashboard/manage_consultants.html", {"consultants": consultants}
    )


@user_passes_test(is_admin)
def add_consultant(request):
    if request.method == "POST":
        form = ConsultantForm(request.POST, request.FILES)
        if form.is_valid():
            consultant = form.save()
            messages.success(
                request,
                f"Consultant added successfully. Login credentials have been sent to {consultant.user.email}.",
            )
            return redirect("manage_consultants")
    else:
        form = ConsultantForm()
    return render(request, "admin_dashboard/add_consultant.html", {"form": form})


@user_passes_test(is_admin)
def manage_services(request):
    services = Service.objects.all().select_related("consultant")
    return render(
        request, "admin_dashboard/manage_services.html", {"services": services}
    )


@user_passes_test(is_admin)
def add_service(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service added successfully")
            return redirect("manage_services")
    else:
        form = ServiceForm()
    return render(request, "admin_dashboard/add_service.html", {"form": form})


@user_passes_test(is_admin)
def view_appointments(request):
    appointments = (
        Appointment.objects.all()
        .select_related("client__user", "consultant__user", "service")
        .order_by("-start_time")
    )
    return render(
        request, "admin_dashboard/appointments.html", {"appointments": appointments}
    )


@user_passes_test(is_admin)
def appointment_detail(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    return render(
        request, "admin_dashboard/appointment_detail.html", {"appointment": appointment}
    )


@user_passes_test(is_admin)
def manage_payments(request):
    payments = Payment.objects.all().select_related("appointment")
    return render(request, "admin_dashboard/payments.html", {"payments": payments})


@user_passes_test(is_admin)
def verify_payment(request, pk):
    payment = Payment.objects.get(pk=pk)
    payment.status = "confirmed"
    payment.verified_by_admin = True
    payment.save()
    messages.success(request, "Payment verified successfully")
    return redirect("manage_payments")


@user_passes_test(is_admin)
def client_list(request):
    clients = Client.objects.all().select_related("user")
    return render(request, "admin_dashboard/clients.html", {"clients": clients})


@user_passes_test(is_admin)
def client_detail(request, pk):
    client = Client.objects.get(pk=pk)
    appointments = client.appointments.all()
    return render(
        request,
        "admin_dashboard/client_detail.html",
        {"client": client, "appointments": appointments},
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Consultant, Availability, Appointment, Service
from .forms import AppointmentForm


@login_required
def consultant_list(request):
    consultants = Consultant.objects.filter(is_active=True)
    return render(request, "booking/consultant_list.html", {"consultants": consultants})


@login_required
def consultant_detail(request, pk):
    consultant = get_object_or_404(Consultant, pk=pk)
    services = consultant.services.all()

    # Get available time slots
    today = timezone.now().date()
    end_date = today + timedelta(days=14)  # Show availability for 2 weeks

    # Get consultant's availability
    availability = {}
    for day in Availability.objects.filter(consultant=consultant):
        availability[day.day_of_week] = {
            "start_time": day.start_time,
            "end_time": day.end_time,
            "is_peak_hour": day.is_peak_hour,
        }

    return render(
        request,
        "booking/consultant_detail.html",
        {
            "consultant": consultant,
            "services": services,
            "availability": availability,
            "date_range": [
                today + timedelta(days=i) for i in range((end_date - today).days + 1)
            ],
        },
    )


from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from .models import MpesaTransaction
from django_daraja.mpesa.core import MpesaClient
from django.db import transaction
import random
import string


@login_required
def create_appointment(request, consultant_pk):
    consultant = get_object_or_404(Consultant, pk=consultant_pk)

    if request.method == "POST":
        form = AppointmentForm(request.POST, consultant=consultant)
        if form.is_valid():
            # Check if the slot is still available
            start_time = form.cleaned_data["start_time"]
            existing_appointments = Appointment.objects.filter(
                consultant=consultant,
                start_time=start_time,
                status__in=["pending", "confirmed"],
            )

            if existing_appointments.exists():
                messages.error(
                    request,
                    "This time slot has already been booked. Please choose another time.",
                )
                return redirect("create_appointment", consultant_pk=consultant.pk)

            # Generate Google Meet link if virtual
            meet_link = ""
            if form.cleaned_data["mode"] == "virtual":
                random_str = "".join(
                    random.choices(string.ascii_letters + string.digits, k=16)
                )
                meet_link = f"https://meet.google.com/{random_str}"

            # Create appointment
            duration_minutes = 60  # or consultant.duration_minutes

            with transaction.atomic():
                appointment = form.save(commit=False)
                appointment.client = request.user.client_profile
                appointment.consultant = consultant
                appointment.meet_link = meet_link
                appointment.start_time = start_time
                appointment.end_time = start_time + timedelta(minutes=duration_minutes)
                appointment.status = "pending"  # Wait for payment confirmation
                appointment.save()

                # Create payment record
                amount = (
                    consultant.hourly_rate * Decimal(duration_minutes) / Decimal(60)
                )
                payment = Payment.objects.create(
                    appointment=appointment,
                    amount=amount,
                    method="mpesa",
                    status="pending",
                )

                # Generate a unique transaction ID (even if payment fails)
                transaction_id = f"MPESA{random.randint(100000, 999999)}"

                # Create M-Pesa transaction record (before initiating payment)
                mpesa_transaction = MpesaTransaction.objects.create(
                    transaction_id=transaction_id,
                    payment=payment,
                    amount=amount,
                    phone_number=request.user.client_profile.phone,
                    status="pending",
                )
                # meet_link = (
                #     appointment.meet_link if appointment.mode == "virtual" else None
                # )
                send_booking_emails(appointment, meet_link)
                # Redirect to payment page with appointment ID
                return redirect("process_payment", appointment_id=appointment.pk)
    else:
        form = AppointmentForm(consultant=consultant)

    return render(
        request,
        "booking/create_appointment.html",
        {"form": form, "consultant": consultant},
    )


@login_required
def process_payment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, client__user=request.user
    )
    payment = appointment.payment

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")

        # Update phone number if different from profile
        if phone_number != request.user.client_profile.phone:
            request.user.client_profile.phone = phone_number
            request.user.client_profile.save()

        mpesa_client = MpesaClient()
        amount = int(payment.amount)  # M-Pesa requires integer amounts

        try:
            # Get the existing transaction record
            mpesa_transaction = payment.mpesa_transactions.first()

            # Initiate STK push
            response = mpesa_client.stk_push(
                phone_number,
                amount,
                f"APPT-{appointment_id}",
                f"Payment for appointment with {appointment.consultant.user.get_full_name()}",
                callback_url="https://darajambili.herokuapp.com/express-payment",
            )

            # Update transaction with response details
            mpesa_transaction.checkout_request_id = response.checkout_request_id
            mpesa_transaction.merchant_request_id = response.merchant_request_id
            mpesa_transaction.response_code = response.response_code
            mpesa_transaction.response_description = response.response_description
            mpesa_transaction.save()

            # Send user to payment processing page
            return redirect("booking_success", appointment_id=appointment_id)

        except Exception as e:
            # Update transaction as failed
            mpesa_transaction.status = "failed"
            mpesa_transaction.result_description = str(e)
            mpesa_transaction.save()

            messages.error(request, f"Payment initiation failed: {str(e)}")
            return redirect("process_payment", appointment_id=appointment_id)

    return render(request, "booking/payment.html", {"appointment": appointment})


@login_required
def payment_processing(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, client__user=request.user
    )
    mpesa_transaction = appointment.payment.mpesa_transactions.first()

    return render(
        request,
        "booking/payment_processing.html",
        {"appointment": appointment, "transaction": mpesa_transaction},
    )


@login_required
def payment_callback(request):
    # This would handle the callback from M-Pesa
    # Implementation depends on your django-daraja version
    pass


def send_booking_emails(appointment, meet_link=None):
    # Email to client
    client_subject = (
        f"Appointment Confirmation with {appointment.consultant.user.get_full_name()}"
    )
    client_message = f"""
    Dear {appointment.client.user.get_full_name()},
    
    Your appointment with {appointment.consultant.user.get_full_name()} has been confirmed.
    
    Details:
    - Date & Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}
    - Service: {appointment.service.name if appointment.service else 'General Consultation'}
    - Mode: {'Virtual' if appointment.mode == 'virtual' else 'In-Person'}
    
    """

    if appointment.mode == "virtual" and meet_link:
        client_message += f"\nYour Google Meet link: {meet_link}\n"
    else:
        client_message += f"\nMeeting Location: our office \n"

    send_mail(
        client_subject,
        client_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.client.user.email],
        fail_silently=False,
    )

    # Email to consultant
    consultant_subject = (
        f"New Appointment with {appointment.client.user.get_full_name()}"
    )
    consultant_message = f"""
    You have a new appointment with {appointment.client.user.get_full_name()}.
    
    Details:
    - Date & Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}
    - Service: {appointment.service.name if appointment.service else 'General Consultation'}
    - Mode: {'Virtual' if appointment.mode == 'virtual' else 'In-Person'}
    - Client Phone: {appointment.client.phone}
    
    """

    if appointment.mode == "virtual" and meet_link:
        consultant_message += f"\nGoogle Meet link: {meet_link}\n"

    send_mail(
        consultant_subject,
        consultant_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.consultant.user.email],
        fail_silently=False,
    )


@login_required
def booking_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, "booking/success.html", {"appointment": appointment})


@login_required
def user_profile(request):
    client = request.user.client_profile
    appointments = client.appointments.all().order_by("-start_time")
    payments = Payment.objects.filter(appointment__client=client).order_by(
        "-payment_date"
    )

    # Stats
    upcoming_appointments = appointments.filter(
        start_time__gte=timezone.now(), status="confirmed"
    ).count()
    completed_appointments = appointments.filter(status="completed").count()
    total_spent = sum(p.amount for p in payments.filter(status="confirmed"))

    return render(
        request,
        "profile/user_profile.html",
        {
            "client": client,
            "appointments": appointments,
            "payments": payments,
            "upcoming_appointments": upcoming_appointments,
            "completed_appointments": completed_appointments,
            "total_spent": total_spent,
        },
    )


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment, pk=pk, client=request.user.client_profile
    )
    return render(
        request, "profile/appointment_detail.html", {"appointment": appointment}
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Consultant, Appointment, Service, Availability, Notification
from .forms import ConsultantProfileForm


@login_required
def consultant_dashboard(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")  # Or appropriate redirect

    consultant = request.user.consultant_profile
    upcoming_appointments = Appointment.objects.filter(
        consultant=consultant, start_time__gte=timezone.now(), status="confirmed"
    ).order_by("start_time")[:5]

    notifications = Notification.objects.filter(user=request.user, read=False).order_by(
        "-created_at"
    )[:5]

    context = {
        "consultant": consultant,
        "upcoming_appointments": upcoming_appointments,
        "notifications": notifications,
    }
    return render(request, "consultant/dashboard.html", context)


@login_required
def consultant_profile(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    consultant = request.user.consultant_profile
    return render(request, "consultant/profile.html", {"consultant": consultant})


@login_required
def update_profile(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    consultant = request.user.consultant_profile

    if request.method == "POST":
        form = ConsultantProfileForm(request.POST, request.FILES, instance=consultant)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("consultant_profile")
    else:
        form = ConsultantProfileForm(instance=consultant)

    return render(request, "consultant/update_profile.html", {"form": form})


@login_required
def appointment_list(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    consultant = request.user.consultant_profile
    upcoming = Appointment.objects.filter(
        consultant=consultant, start_time__gte=timezone.now()
    ).order_by("start_time")

    past = Appointment.objects.filter(
        consultant=consultant, start_time__lt=timezone.now()
    ).order_by("-start_time")

    context = {
        "upcoming_appointments": upcoming,
        "past_appointments": past,
    }
    return render(request, "consultant/appointments.html", context)


@login_required
def mark_appointment_completed(request, pk):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    appointment = get_object_or_404(
        Appointment, pk=pk, consultant=request.user.consultant_profile
    )

    if appointment.status != "completed":
        appointment.status = "completed"
        appointment.save()
        messages.success(request, "Appointment marked as completed.")

    return redirect("consultant_appointments")


@login_required
def availability_list(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    consultant = request.user.consultant_profile
    availabilities = Availability.objects.filter(consultant=consultant).order_by(
        "day_of_week", "start_time"
    )

    # Add this line to create a form instance
    form = AvailabilityForm()

    context = {
        "availabilities": availabilities,
        "form": form,  # Make sure to include the form in context
    }
    return render(request, "consultant/availability.html", context)


@login_required
def service_list(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    consultant = request.user.consultant_profile
    services = Service.objects.filter(consultant=consultant)

    context = {
        "services": services,
    }
    return render(request, "consultant/services.html", context)


@login_required
def notification_list(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    context = {
        "notifications": notifications,
    }
    return render(request, "consultant/notifications.html", context)


@login_required
def mark_notifications_read(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect("consultant_notifications")


@login_required
def add_availability(request):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    if request.method == "POST":
        consultant = request.user.consultant_profile
        day_of_week = request.POST.get("day_of_week")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        is_peak_hour = request.POST.get("is_peak_hour") == "on"

        try:
            Availability.objects.create(
                consultant=consultant,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_peak_hour=is_peak_hour,
            )
            messages.success(request, "Availability slot added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding availability: {str(e)}")

        return redirect("consultant_availability")

    return redirect("consultant_availability")


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Availability
from .forms import AvailabilityForm


class AvailabilityListView(ListView):
    model = Availability
    template_name = "availability.html"
    context_object_name = "availabilities"

    def get_queryset(self):
        return Availability.objects.filter(
            consultant=self.request.user.consultant_profile
        )


class AvailabilityCreateView(CreateView):
    model = Availability
    form_class = AvailabilityForm
    template_name = "modals/availability_form.html"
    success_url = reverse_lazy("consultant_availability")

    def form_valid(self, form):
        form.instance.consultant = self.request.user.consultant_profile
        return super().form_valid(form)


class AvailabilityUpdateView(UpdateView):
    model = Availability
    form_class = AvailabilityForm
    template_name = "modals/availability_form.html"
    success_url = reverse_lazy("consultant_availability")


class AvailabilityDeleteView(DeleteView):
    model = Availability
    template_name = "modals/availability_confirm_delete.html"
    success_url = reverse_lazy("consultant_availability")


@login_required
def delete_availability(request, pk):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    availability = get_object_or_404(
        Availability, pk=pk, consultant=request.user.consultant_profile
    )

    if request.method == "POST":
        availability.delete()
        messages.success(request, "Availability slot deleted successfully!")
        return redirect("consultant_availability")

    return redirect("consultant_availability")


@login_required
def add_service(request):
    if not hasattr(request.user, "consultant_profile") and not request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        consultant = request.user.consultant_profile
        name = request.POST.get("name")
        description = request.POST.get("description")

        try:
            Service.objects.create(
                name=name, description=description, consultant=consultant
            )
            messages.success(request, "Service added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding service: {str(e)}")

        return redirect("consultant_services")

    return redirect("consultant_services")


@login_required
def edit_service(request, pk):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    service = get_object_or_404(
        Service, pk=pk, consultant=request.user.consultant_profile
    )

    if request.method == "POST":
        service.name = request.POST.get("name")
        service.description = request.POST.get("description")
        service.save()
        messages.success(request, "Service updated successfully!")
        return redirect("consultant_services")

    return redirect("consultant_services")


@login_required
def delete_service(request, pk):
    if not hasattr(request.user, "consultant_profile"):
        return redirect("access_denied")

    service = get_object_or_404(
        Service, pk=pk, consultant=request.user.consultant_profile
    )

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted successfully!")
        return redirect("consultant_services")

    return redirect("consultant_services")


# from django_daraja.mpesa.core import MpesaClient
# from django.db import transaction
# @transaction.atomic
# def account(request):
#     hotel = Hotel.objects.all()
#     current_user = request.user
#     user_reminders = Reminder.objects.filter(user=current_user)
#     user_booking = Booking.objects.filter(user=current_user)
#     cart = Cart(request)
#     bkd_room = {}
#     hot = get_object_or_404(Hotel, pk=1)
#     hotel_name = hot.name
#     if request.method == "POST":

#         phone_number = request.POST.get("phone_number")
#         am = request.POST.get("amount")
#         amn = float(am)
#         amount = round(amn)
#         account_reference = f"{hotel_name}"
#         transaction_desc = f"Payment for booking"

#         mpesa_client = MpesaClient()

#         try:
#             response = mpesa_client.stk_push(
#                 phone_number,
#                 amount,
#                 account_reference,
#                 transaction_desc,
#                 callback_url="https://darajambili.herokuapp.com/express-payment",
#                 # callback_url=settings.MPESA_CALLBACK_URL,
#             )

#         except Exception as e:
#             return f"Mpesa payment initiation failed: {str(e)}"

#         phone_number_instance, created = PhoneNumber.objects.get_or_create(
#             phone_number=phone_number
#         )

#         for room in cart:
#             current_b = Booking.objects.create(
#                 user=current_user,
#                 room=room["room"],
#                 check_in_date=room["start_date"],
#                 check_out_date=room["end_date"],
#                 total_price=room["total_price"],
#                 payment_status="paid",
#             )
#             booking_instance = current_b
#             MPesaTransaction.objects.create(
#                 transaction_id=response.checkout_request_id,
#                 booking=booking_instance,
#                 amount=amount,
#                 phone_number=phone_number_instance,
#                 status="Pending",
#             )

#             RoomAvailability.objects.create(
#                 room=room["room"],
#                 start_date=room["start_date"],
#                 end_date=room["end_date"],
#             )
#             room_name = room["room"]
#             bkd_room[room_name] = {
#                 "start_date": room["start_date"],
#                 "end_date": room["end_date"],
#             }
#         rooms_info = "; ".join(
#             [
#                 f"{room}: {details['start_date']} - {details['end_date']}"
#                 for room, details in bkd_room.items()
#             ]
#         )
#         cart.clear()

#         subject = "SUCCESFUL ROOM BOOKING"
#         message = (
#             f"JAMBO! {current_user.username},"
#             f"Your booking with {hotel_name} has been successfull. "
#             f"Rooms booked:\n{rooms_info}"
#             f"Experience luxury at its best. WELCOME!\n\n"
#         )
#         from_email = settings.EMAIL_HOST_USER
#         to_email = [current_user.email]

#         send_booking_email.delay(
#             subject,
#             message,
#             from_email,
#             to_email,
#         )

#         # response_des = response.response_description
#         # response_data = {"response_des": response_des}
#         # return JsonResponse(response_data, safe=False)
#     return render(
#         request,
#         "service/res/account.html",
#         {"rmb": user_reminders, "hotel": hotel, "book": user_booking},
#     )
