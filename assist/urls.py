from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Auth Views
    path("", views.home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register_client, name="register"),
    path("services/", views.services, name="services"),
    path("consultants/", views.consultants, name="consultants"),
    path("contact/", views.contact, name="contact"),
    # path('profile/', views.profile, name='profile'),
    # path('appointments/', appointment_views.my_appointments, name='my_appointments'),
    path("ad_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("ad/consultants/", views.manage_consultants, name="manage_consultants"),
    path("ad/consultants/add/", views.add_consultant, name="add_consultant"),
    path("ad/services/", views.manage_services, name="manage_services"),
    path("ad/services/add/", views.add_service, name="add_service"),
    path("appointments/", views.view_appointments, name="view_appointments"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("payments/", views.manage_payments, name="manage_payments"),
    path("payments/<int:pk>/verify/", views.verify_payment, name="verify_payment"),
    path("clients/", views.client_list, name="client_list"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("user/consultants/", views.consultant_list, name="consultant_list"),
    path(
        "user/consultants/<int:pk>/", views.consultant_detail, name="consultant_detail"
    ),
    path(
        "user/consultants/<int:consultant_pk>/book/",
        views.create_appointment,
        name="create_appointment",
    ),
    # Profile URLs
    path("profile/", views.user_profile, name="user_profile"),
    path(
        "profile/appointments/<int:pk>/",
        views.appointment_detail,
        name="appointment_detail",
    ),
    path(
        "consultant/dashboard/", views.consultant_dashboard, name="consultant_dashboard"
    ),
    path("consultant/profile/", views.consultant_profile, name="consultant_profile"),
    path(
        "consultant/profile/update/",
        views.update_profile,
        name="update_consultant_profile",
    ),
    path(
        "consultant/appointments/",
        views.appointment_list,
        name="consultant_appointments",
    ),
    path(
        "consultant/appointments/<int:pk>/complete/",
        views.mark_appointment_completed,
        name="mark_appointment_completed",
    ),
    path(
        "consultant/availability/",
        views.availability_list,
        name="consultant_availability",
    ),
    path(
        "consultant.availability/add/", views.add_availability, name="add_availability"
    ),
    path(
        "consultant/availability/<int:pk>/delete/",
        views.delete_availability,
        name="delete_availability",
    ),
    path(
        "availability/add/",
        views.AvailabilityCreateView.as_view(),
        name="availability_create",
    ),
    path(
        "availability/<int:pk>/edit/",
        views.AvailabilityUpdateView.as_view(),
        name="availability_update",
    ),
    path(
        "availability/<int:pk>/delete/",
        views.AvailabilityDeleteView.as_view(),
        name="availability_delete",
    ),
    path("consultant/services/", views.service_list, name="consultant_services"),
    path("consultant/services/<int:pk>/edit/", views.edit_service, name="edit_service"),
    path(
        "consultant/services/<int:pk>/delete/",
        views.delete_service,
        name="delete_service",
    ),
    path(
        "consultant/notifications/",
        views.notification_list,
        name="consultant_notifications",
    ),
    path(
        "consultant/notifications/mark-read/",
        views.mark_notifications_read,
        name="mark_notifications_read",
    ),
    path(
        "booking/success/<int:appointment_id>/",
        views.booking_success,
        name="booking_success",
    ),
    path(
        "payment/<int:appointment_id>/", views.process_payment, name="process_payment"
    ),
    path(
        "payment-processing/<int:appointment_id>/",
        views.payment_processing,
        name="payment_processing",
    ),
    # path("mpesa-callback/", views.payment_callback, name="mpesa_callback"),
    # path('consultant/<int:pk>/', views.ConsultantDetailView.as_view(), name='consultant_detail'),
    # path('consultant/<int:pk>/book/', views.BookAppointmentView.as_view(), name='book_appointment'),
]
