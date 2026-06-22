from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, DonorViewSet, BloodRequestViewSet

# إنشاء الـ Router وتسجيل الـ ViewSets فيه
router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'donors', DonorViewSet)
router.register(r'requests', BloodRequestViewSet)

# الروابط المتاحة للتطبيق
urlpatterns = [
    path('', include(router.urls)),
]