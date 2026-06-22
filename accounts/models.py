from django.db import models
from django.contrib.auth.models import User

# Hospitals table
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True) 
    city = models.CharField(max_length=100)
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
    city = models.CharField(max_length=100)
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