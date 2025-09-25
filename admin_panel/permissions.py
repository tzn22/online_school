from rest_framework import permissions

class IsAdminOnly(permissions.BasePermission):
    """
    Разрешение только администраторам
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение только администраторам на запись
    """
    def has_permission(self, request, view):
        # Разрешаем чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Запись только администраторам
        return request.user.is_authenticated and request.user.is_admin

class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешение администраторам или владельцу объекта
    """
    def has_object_permission(self, request, view, obj):
        # Администратор может всё
        if request.user.is_admin:
            return True
        # Владелец может всё со своим объектом
        return obj.created_by == request.user

class CanViewAdminPanel(permissions.BasePermission):
    """
    Разрешение на просмотр админ панели
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or 
            request.user.is_teacher or
            request.user.is_manager
        )

class CanManageSystemSettings(permissions.BasePermission):
    """
    Разрешение на управление системными настройками
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin

class CanSendMassEmail(permissions.BasePermission):
    """
    Разрешение на отправку массовых email
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class CanGenerateReports(permissions.BasePermission):
    """
    Разрешение на генерацию отчетов
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or
            request.user.is_manager
        )