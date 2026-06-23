from django.db import models
from django.contrib.auth.models import User

CITY_CHOICES = [
    ('Amman', 'عمان'),
    ('Irbid', 'إربد'),
    ('Zarqa', 'الزرقاء'),
    ('Mafraq', 'المفرق'),
    ('Jerash', 'جرش'),
    ('Ajloun', 'عجلون'),
    ('Salt', 'السلط (البلقاء)'),
    ('Madaba', 'مأدبا'),
    ('Karak', 'الكرك'),
    ('Tafilah', 'الطفيلة'),
    ('Ma\'an', 'معان'),
    ('Aqaba', 'العقبة'),
]

# Hospitals table
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True) 
    city = models.CharField(
        max_length=50, 
        choices=CITY_CHOICES, 
        default='Amman'
    )
    address = models.TextField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Donors table
class Donor(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    city = models.CharField(
        max_length=50, 
        choices=CITY_CHOICES, 
        default='Amman'
    )
    phone_number = models.CharField(max_length=20)
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.user.username} ({self.blood_type})"

# Blood Requests table
class BloodRequest(models.Model):
    URGENCY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('CRITICAL', 'Critical'), 
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='requests')
    blood_type = models.CharField(max_length=3, choices=Donor.BLOOD_TYPES)
    units_requested = models.PositiveIntegerField(default=1) 
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.hospital.name} needs {self.blood_type} ({self.urgency})"

# Donation Transactions table 
class DonationTransaction(models.Model):
    TRANSACTION_STATUS = [
        ('INTERESTED', 'Interested'), 
        ('DONATED', 'Donated Successfully'), 
        ('REJECTED', 'Medical Rejection'), 
    ]

    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='matches')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='my_donations')
    status = models.CharField(max_length=15, choices=TRANSACTION_STATUS, default='INTERESTED')
    action_date = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.donor.user.username} -> {self.blood_request.id} ({self.status})"
    

class Notification(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    #  ربط الإشعار بطلب الدم المعني (بحيث لو حُذف الطلب، يُحذف الإشعار تلقائياً)
    blood_request = models.ForeignKey('BloodRequest', on_delete=models.CASCADE, related_name='notifications')
    
    #  نص الرسالة التي ستظهر للمتبرع
    message = models.TextField()
    
    #  حالة الإشعار (هل قرأه المتبرع أم لا؟) لكي نُظهر له نقطة حمراء أو عداد للإشعارات الجديدة
    is_read = models.BooleanField(default=False)
    
    #  وقت إرسال الإشعار لترتيبها من الأحدث للأقدم
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - Read: {self.is_read}" 
       
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

@receiver(post_save, sender=BloodRequest)
def send_notifications_on_new_request(sender, instance, created, **kwargs):
    """
    هذه الإشارة تعمل تلقائياً فور حفظ أي طلب دم جديد في قاعدة البيانات
    سواء من الـ API أو من لوحة الـ Admin!
    """
    if created: # التحقق من أن العملية هي إنشاء طلب جديد وليس تعديل طلب قديم
        blood_request = instance
        hospital_profile = blood_request.hospital
        
        if not hospital_profile:
            return

        requested_type = blood_request.blood_type
        hospital_city = hospital_profile.city

        # الخريطة الطبية للتوافق
        compatibility_map = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-'],
        }
        compatible_types = compatibility_map.get(requested_type, [requested_type])
        safe_donation_date = timezone.now().date() - timedelta(days=90)

        # جلب المتبرعين المستهدفين
        matching_donors = Donor.objects.filter(
            blood_type__in=compatible_types,
            city__iexact=hospital_city,
            is_available=True
        ).filter(
            Q(last_donation_date__lte=safe_donation_date) | Q(last_donation_date__isnull=True)
        )

        # إنشاء الإشعارات في قاعدة البيانات
        for donor in matching_donors:
            Notification.objects.create(
                user=donor.user,
                blood_request=blood_request,
                message=f"نداء إنساني عاجل! مستشفى {hospital_profile.name} بحاجة ماسة لفصيلة دم {requested_type}. هل يمكنك المساعدة؟"
            )    
@receiver(post_save, sender=DonationTransaction)
def update_donor_last_donation_date(sender, instance, created, **kwargs):
    """
    إشارة تتحقق أن حالة التبرع أصبحت مكتملة فعلياً (Donated)
    لتحديث تواريخ المتبرعين وإرسال الإشعارات تلقائياً.
    """
    if instance.status.upper() == 'DONATED' or instance.status == 'Completed':
        donor_profile = instance.donor
        from django.utils import timezone
        
        # 1️⃣ تحديث تاريخ آخر تبرع للبطل إلى تاريخ اليوم
        donor_profile.last_donation_date = timezone.now().date()
        donor_profile.save()
        
        # 2️⃣ إرسال إشعار الشكر تلقائياً (مع فحص التكرار)
        notification_exists = Notification.objects.filter(
            user=donor_profile.user,
            blood_request=instance.blood_request,
            message__contains="شكراً لك من القلب"
        ).exists()
        
        if not notification_exists:
            Notification.objects.create(
                user=donor_profile.user,
                blood_request=instance.blood_request,
                message=f"شكراً لك من القلب! تم تسجيل عملية تبرعك بنجاح لصالح مستشفى {instance.blood_request.hospital.name}. دمك أنقذ حياة إنسان وفي ميزان حسناتك. 🩸❤️"
            )