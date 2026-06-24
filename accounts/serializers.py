from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Hospital, Donor, BloodRequest, DonationTransaction
from .models import Notification

# 1️⃣ مسلسِل بيانات المستخدم الأساسي (User Serializer)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
# 2️⃣ مسلسِل بيانات المستشفيات (Hospital Serializer)
class HospitalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # التعديل هنا: حذفنا الحقل الخاطئ وتركنا read_only

    class Meta:
        model = Hospital
        fields = ['id', 'user', 'name', 'license_number', 'city', 'address', 'phone_number']

# 3️⃣ مسلسِل بيانات المتبرعين (Donor Serializer)
class DonorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Donor
        fields = ['id', 'user', 'blood_type', 'city', 'phone_number', 'last_donation_date', 'is_available']

# 4️⃣ مسلسِل طلبات الدم (Blood Request Serializer)
class BloodRequestSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source='hospital.name', read_only=True) # لعرض اسم المستشفى مباشرة بدل الآي دي

    class Meta:
        model = BloodRequest
        fields = ['id', 'hospital', 'hospital_name', 'blood_type', 'units_requested', 'urgency', 'status', 'created_at']
        read_only_fields = ['hospital'] # إخبار دجانقو بأن هذا الحقل يُحقن من السيرفر ولا ينتظر مدخلات من المستخدم

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'blood_request']
        # حماية البيانات من التعديل العبثي عبر الـ API، فقط يسمح بتغيير is_read
        read_only_fields = ['id', 'message', 'created_at', 'blood_request']