import pytest
from django.contrib.auth import get_user_model
from accounts.models import BloodRequest, Notification, Hospital, Donor 

User = get_user_model()

@pytest.mark.django_db
def test_notification_created_on_blood_request_save():
    # 1️⃣ تجهيز حساب وملف المستشفى (Hospital Setup)
    hospital_user = User.objects.create_user(
        username="test_hospital_user", 
        password="password123",
        email="hospital@test.com"
    )
    hospital_profile = Hospital.objects.create(
        user=hospital_user,
        name="مستشفى البشير",
        license_number="HOSP-12345",
        city="Amman",  # المدينة: عمان
        phone_number="0790000000"
    )
    
    # 2️⃣ تجهيز حساب وملف المتبرع المتوافق (Donor Setup)
    donor_user = User.objects.create_user(
        username="test_donor_user",
        password="password123",
        email="donor@test.com"
    )
    donor_profile = Donor.objects.create(
        user=donor_user,
        blood_type="A+",  # فصيلة متوافقة مع طلب A+
        city="Amman",     # نفس المدينة لضمان عمل الفلتر بنجاح ✨
        phone_number="0780000000",
        is_available=True
    )
    
    # التأكد أن جدول الإشعارات فارغ تماماً قبل توليد الطلب
    assert Notification.objects.count() == 0

    # 3️⃣ التنفيذ (Action): إنشاء طلب دم جديد من المستشفى
    blood_request = BloodRequest.objects.create(
        hospital=hospital_profile,
        blood_type="A+",
        units_requested=2,
        urgency="CRITICAL"
    )

    # 4️⃣ التحقق (Assert): هل قام الـ Signal بالتقاط التطابق بنجاح؟
    # بما أن المتبرع في نفس المدينة ودمه متوافق، يجب أن يصبح الإشعار = 1
    assert Notification.objects.count() == 1
    
    # التحقق من أن محتوى رسالة الإشعار يخص المتبرع وطلب الدم الصحيح
    generated_notification = Notification.objects.first()
    assert generated_notification.user == donor_user
    assert generated_notification.blood_request == blood_request
    assert "مستشفى البشير" in generated_notification.message