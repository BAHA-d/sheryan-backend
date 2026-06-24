"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.view_site if hasattr(admin.site, 'view_site') else admin.site.urls),
    path('api/', include('accounts.urls')), # ربط روابط مشروع شريان وتبدأ بـ api/

    # السطر الجديد: يسمح لك بتسجيل الدخول مباشرة من واجهة الـ API بالمتصفح
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # روابط الحماية وتوليد التوكن
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # لتسجيل الدخول والحصول على التوكن
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # لتحديث التوكن المنتهي
    #روابط التوثيق
    # 1. رابط لتوليد ملف الـ Schema (ملف الـ JSON الأساسي)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. رابط واجهة Swagger التفاعلية الرائعة
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. رابط واجهة ReDoc الأنيقة (شكل بديل ومنظم جداً للقراءة)
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
