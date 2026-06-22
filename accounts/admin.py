from django.contrib import admin
from .models import Hospital, Donor, BloodRequest, DonationTransaction

# تسجيل الجداول لتظهر في لوحة التحكم
admin.site.register(Hospital)
admin.site.register(Donor)
admin.site.register(BloodRequest)
admin.site.register(DonationTransaction)