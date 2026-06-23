from django.contrib import admin
from .models import Hospital, Donor, BloodRequest, DonationTransaction, Notification
# تسجيل الجداول لتظهر في لوحة التحكم
admin.site.register(Hospital)
admin.site.register(Donor)
admin.site.register(BloodRequest)
admin.site.register(DonationTransaction)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_request', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']
# @admin.register(DonationTransaction)
class DonationTransactionAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_request', 'transaction_date']  