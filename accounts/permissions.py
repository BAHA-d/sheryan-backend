from rest_framework import permissions

class IsHospitalUser(permissions.BasePermission):
    """
    صلاحية مخصصة تسمح فقط للمستشفيات بإنشاء أو تعديل البيانات،
    بينما تسمح بالقراءة فقط (GET) لبقية المستخدمين المسجلين.
    """
    def has_permission(self, request, view):
        # 1. إذا كان الطلب للقراءة فقط (GET, HEAD, OPTIONS) يسمح للجميع المسجلين
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 2. إذا كان الطلب تعديل أو إضافة (POST, PUT, DELETE)، نتأكد أن المستخدم مسجل ولديه ملف مستشفى
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'hospital_profile')
        )