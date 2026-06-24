from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, DonorViewSet, BloodRequestViewSet
from .views import NotificationViewSet #حيث يوجد الـ Routers

# إنشاء الـ Router وتسجيل الـ ViewSets فيه
router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'donors', DonorViewSet)
router.register(r'requests', BloodRequestViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
# الروابط المتاحة للتطبيق
urlpatterns = [
    path('', include(router.urls)),
]
