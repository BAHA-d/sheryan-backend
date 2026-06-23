from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Hospital, Donor, BloodRequest
from .serializers import HospitalSerializer, DonorSerializer, BloodRequestSerializer
from .permissions import IsHospitalUser # استيراد الصلاحية الجديدة

# 1️⃣ الـ View الخاص بالمستشفيات
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated] # يجب أن يكون مسجلاً دخولاً برقم سري وتوكن لرؤيتها

# 2️⃣ الـ View الخاص بالمتبرعين
class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [IsAuthenticated]

# 3️⃣ الـ View الخاص بطلبات الدم
class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer
    permission_classes = [IsHospitalUser] # تطبيق الصلاحية المخصصة التي كتبناها بالأعلى
    def perform_create(self, serializer):
        # جلب ملف المستشفى المرتبط بحساب المستخدم الذي قام بتسجيل الدخول حالياً وحفظه تلقائياً
        hospital_profile = self.request.user.hospital_profile
        serializer.save(hospital=hospital_profile)