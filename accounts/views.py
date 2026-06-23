from rest_framework import viewsets,status 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Hospital, Donor, BloodRequest
from .serializers import HospitalSerializer, DonorSerializer, BloodRequestSerializer
from .permissions import IsHospitalUser # استيراد الصلاحية الجديدة
from django.utils import timezone
from datetime import timedelta

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
        # 🗓️ حساب تاريخ الأمان الطبي (90 يوماً قبل الآن)
    
        safe_donation_date = timezone.now().date() - timedelta(days=90)

        # 3. الاستعلام الذكي (Query) من قاعدة البيانات:
        # فحص المتبرعين الذين يمتلكون فصيلة متوافقة وَ متواجدين في نفس مدينة المستشفى
       # 3. 🎯 الاستعلام المحدث بـ تفاصيل التفاصيل الطبية والجغرافية:
        from django.db.models import Q
        matching_donors = Donor.objects.filter(
            blood_type__in=compatible_types,
            city__iexact=hospital_city,
            is_available=True, #  الشرط 1: الحساب متاح ونشط
        ).filter(
            #  الشرط 2: مر على تبرعه أكثر من 90 يوم أو لم يسبق له التبرع مطلقاً
            Q(last_donation_date__lte=safe_donation_date) | Q(last_donation_date__isnull=True)
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
    #  الرابط المخصص الثاني: api/requests/{id}/complete/
    @action(detail=True, methods=['post'], permission_classes=[IsHospitalUser])
    def complete(self, request, pk=None):
        """
        تسمح للمستشفى (صاحب الطلب) بتغيير حالة الطلب إلى مكتمل (Completed).
        """
        blood_request = self.get_object()
        
        #  فحص أمني صارم: هل المستشفى الحالي هو صاحب الطلب؟
        if blood_request.hospital != request.user.hospital_profile:
            return Response(
                {"detail": "غير مسموح لك بتعديل طلب تابع لمستشفى آخر."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # تحديث الحالة وحفظها
        blood_request.status = 'Completed'
        blood_request.save()
        
        return Response({
            "message": "تم إغلاق طلب الدم بنجاح واكتمال وحدات التبرع.",
            "status": blood_request.status
        }, status=status.HTTP_200_OK)
    


    def get_queryset(self):
        # 1. جلب الوقت الحالي
        now = timezone.now()
        # تحديد عتبة الوقت (قبل 48 ساعة من الآن)
        expiry_threshold = now - timedelta(days=2)
        
        # 2. أتمتة ذكية: جلب كل الطلبات المعلقة التي تجاوزت 48 ساعة وتحديثها إلى Expired دفعة واحدة بكفاءة
        BloodRequest.objects.filter(
            status='Pending',
            created_at__lt=expiry_threshold
        ).update(status='Expired')
        
        # 3. إرجاع القائمة كاملة بعد التحديث
        return BloodRequest.objects.all().order_by('-created_at')