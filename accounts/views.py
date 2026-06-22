from rest_framework import viewsets
from .models import Hospital, Donor, BloodRequest
from .serializers import HospitalSerializer, DonorSerializer, BloodRequestSerializer

# 1️⃣ الـ View الخاص بالمستشفيات
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

# 2️⃣ الـ View الخاص بالمتبرعين
class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer

# 3️⃣ الـ View الخاص بطلبات الدم
class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer