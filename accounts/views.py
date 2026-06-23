from rest_framework import viewsets,status 
from rest_framework.decorators import action
from rest_framework.response import Response
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

        #  الرابط المخصص الجديد: api/requests/{id}/matches/
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def matches(self, request, pk=None):
        """
        تبحث عن المتبرعين المتوافقين طبياً وجغرافياً مع هذا الطلب المحدد.
        """
        # 1. جلب طلب الدم الحالي بناءً على الـ ID (pk)
        blood_request = self.get_object()
        requested_type = blood_request.blood_type
        hospital_city = blood_request.hospital.city # جلب مدينة المستشفى التي طلبت الدم

        # 2. القاموس الطبي الذكي لتوافق فصائل الدم (من يمكنه التبرع لمن؟)
        # المفتاح: الفصيلة المطلوبة -> القيمة: قائمة الفصائل التي يمكنها التبرع لها
        compatibility_map = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], # يستقبل من الجميع
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-'], # لا يستقبل إلا من فصيلته ولكنه يعطي الجميع
        }

        # جلب الفصائل المتوافقة مع الطلب الحالي، إذا لم تكن موجودة نكتفي بنفس الفصيلة كأمان
        compatible_types = compatibility_map.get(requested_type, [requested_type])

        # 3. الاستعلام الذكي (Query) من قاعدة البيانات:
        # فحص المتبرعين الذين يمتلكون فصيلة متوافقة وَ متواجدين في نفس مدينة المستشفى
        matching_donors = Donor.objects.filter(
            blood_type__in=compatible_types,
            city__iexact=hospital_city # iexact تقارن النصوص بدون الحساسية لحالة الأحرف (Capital/Small)
        )

        # 4. تحويل بيانات المتبرعين إلى JSON باستخدام الـ Serializer الخاص بهم وإرجاعها
        serializer = DonorSerializer(matching_donors, many=True)
        return Response({
            "requested_blood_type": requested_type,
            "hospital_city": hospital_city,
            "compatible_types_searched": compatible_types,
            "total_matches": matching_donors.count(),
            "matches": serializer.data
        }, status=status.HTTP_200_OK)