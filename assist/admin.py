from django.contrib import admin
from .models import (
    Client,
    Consultant,
    Service,
    Availability,
    Appointment,
    Payment,
    Notification
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone','date_of_birth')
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('user__username',)

@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'hourly_rate', 'is_active')
    search_fields = ('user__username', 'expertise')
    list_filter = ('is_active',)
    ordering = ('user__username',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'consultant')
    search_fields = ('name', 'consultant__user__username')
    list_filter = ('consultant',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('consultant', 'day_of_week', 'start_time', 'end_time', 'is_peak_hour')
    search_fields = ('consultant__user__username', 'day_of_week')
    list_filter = ('day_of_week', 'is_peak_hour')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'consultant', 'start_time', 'end_time', 'mode', 'status')
    search_fields = ('client__user__username', 'consultant__user__username')
    list_filter = ('status', 'mode', 'start_time')
    ordering = ('-start_time',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'amount', 'method', 'status', 'payment_date', 'verified_by_admin')
    search_fields = ('appointment__client__user__username', 'method')
    list_filter = ('status', 'method', 'payment_date')
    readonly_fields = ('payment_date',)
    ordering = ('-payment_date',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read')
    search_fields = ('user__username', 'message')
    list_filter = ('read',)
    ordering = ('-created_at',)



from django.contrib import admin
from .models import MpesaTransaction

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'payment',
        'amount',
        'phone_number',
        'status',
        'transaction_date',
    )
    list_filter = ('status', 'transaction_date')
    search_fields = ('transaction_id', 'phone_number', 'payment__id')
    ordering = ('-transaction_date',)
