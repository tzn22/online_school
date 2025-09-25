from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg
from .models import AdminActionLog, ReportTemplate, GeneratedReport, MassEmailCampaign, SystemSetting
from accounts.models import User
from courses.models import Course, Group, Lesson
from payments.models import Payment
from .serializers import (
    AdminActionLogSerializer,
    ReportTemplateSerializer,
    GeneratedReportSerializer,
    MassEmailCampaignSerializer,
    SystemSettingSerializer
)
from .permissions import IsAdminOnly

# === ADMIN ACTION LOGS ===

class AdminActionLogListView(generics.ListAPIView):
    """Список логов действий администраторов"""
    queryset = AdminActionLog.objects.all()
    serializer_class = AdminActionLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action_type', 'model_name', 'admin_user', 'created_at']
    search_fields = ['description', 'admin_user__username', 'admin_user__email']
    ordering_fields = ['created_at', 'action_type', 'model_name']
    ordering = ['-created_at']

# === REPORT TEMPLATES ===

class ReportTemplateListView(generics.ListCreateAPIView):
    """Список шаблонов отчетов и создание нового шаблона"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'report_type']
    ordering = ['-created_at']

class ReportTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали шаблона отчета"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# === GENERATED REPORTS ===

class GeneratedReportListView(generics.ListCreateAPIView):
    """Список сгенерированных отчетов и создание нового отчета"""
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_template', 'generated_by', 'is_published', 'generated_at']
    search_fields = ['title', 'report_template__name']
    ordering_fields = ['generated_at', 'title']
    ordering = ['-generated_at']

class GeneratedReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали сгенерированного отчета"""
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# === MASS EMAIL CAMPAIGNS ===

class MassEmailCampaignListView(generics.ListCreateAPIView):
    """Список email кампаний и создание новой кампании"""
    queryset = MassEmailCampaign.objects.all()
    serializer_class = MassEmailCampaignSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'target_audience', 'created_by', 'scheduled_at']
    search_fields = ['name', 'subject', 'content']
    ordering_fields = ['created_at', 'scheduled_at', 'status']
    ordering = ['-created_at']

class MassEmailCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали email кампании"""
    queryset = MassEmailCampaign.objects.all()
    serializer_class = MassEmailCampaignSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# === SYSTEM SETTINGS ===

class SystemSettingListView(generics.ListCreateAPIView):
    """Список системных настроек и создание новой настройки"""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['setting_type', 'is_public', 'category']
    search_fields = ['name', 'key', 'description']
    ordering_fields = ['name', 'key', 'category', 'created_at']
    ordering = ['category', 'name']

class SystemSettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали системной настройки"""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# === DASHBOARD AND STATISTICS ===

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard(request):
    """Дашборд администратора"""
    # Статистика пользователей
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'students': User.objects.filter(role='student').count(),
        'teachers': User.objects.filter(role='teacher').count(),
        'parents': User.objects.filter(role='parent').count(),
        'admins': User.objects.filter(role='admin').count(),
    }
    
    # Статистика курсов
    course_stats = {
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects.filter(is_active=True).count(),
        'total_groups': Group.objects.count(),
        'active_groups': Group.objects.filter(is_active=True).count(),
    }
    
    # Статистика платежей
    payment_stats = {
        'total_payments': Payment.objects.count(),
        'paid_payments': Payment.objects.filter(status='paid').count(),
        'total_revenue': float(Payment.objects.filter(status='paid').aggregate(
            Sum('amount')
        )['amount__sum'] or 0),
    }
    
    # Статистика занятий
    lesson_stats = {
        'total_lessons': Lesson.objects.count(),
        'completed_lessons': Lesson.objects.filter(is_completed=True).count(),
        'today_lessons': Lesson.objects.filter(
            start_time__date=timezone.now().date()
        ).count(),
    }
    
    return Response({
        'user_stats': user_stats,
        'course_stats': course_stats,
        'payment_stats': payment_stats,
        'lesson_stats': lesson_stats,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_health_check(request):
    """Проверка состояния системы"""
    from django.db import connection
    from django_redis import get_redis_connection
    
    health_status = {
        'database': 'unknown',
        'redis': 'unknown',
        'web_server': 'unknown',
        'celery': 'unknown',
    }
    
    # Проверка базы данных
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['database'] = 'healthy'
    except Exception as e:
        health_status['database'] = f'unhealthy: {str(e)}'
    
    # Проверка Redis
    try:
        redis_conn = get_redis_connection("default")
        redis_conn.ping()
        health_status['redis'] = 'healthy'
    except Exception as e:
        health_status['redis'] = f'unhealthy: {str(e)}'
    
    # Проверка веб-сервера
    health_status['web_server'] = 'healthy'
    
    # Проверка Celery (если запущен)
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status['celery'] = 'healthy'
        else:
            health_status['celery'] = 'unhealthy: no workers'
    except Exception as e:
        health_status['celery'] = f'unhealthy: {str(e)}'
    
    overall_health = all(status == 'healthy' for status in health_status.values() if isinstance(status, str) and status != 'unknown')
    
    return Response({
        'status': 'healthy' if overall_health else 'unhealthy',
        'components': health_status,
        'timestamp': timezone.now().isoformat(),
    })

# === ACTIONS ===

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def send_mass_email(request):
    """Отправка массового email"""
    serializer = MassEmailCampaignSerializer(data=request.data)
    if serializer.is_valid():
        campaign = serializer.save(created_by=request.user)
        
        # Здесь будет логика отправки email
        # Пока возвращаем заглушку
        
        return Response({
            'message': 'Email кампания создана',
            'campaign': MassEmailCampaignSerializer(campaign).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def generate_report(request):
    """Генерация отчета"""
    report_template_id = request.data.get('report_template_id')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    
    try:
        report_template = ReportTemplate.objects.get(id=report_template_id)
        
        # Здесь будет логика генерации отчета
        # Пока возвращаем заглушку
        
        report = GeneratedReport.objects.create(
            report_template=report_template,
            title=f"{report_template.name} - {period_start} to {period_end}",
            period_start=period_start,
            period_end=period_end,
            generated_by=request.user,
            file_size=1024,  # Заглушка
        )
        
        serializer = GeneratedReportSerializer(report)
        return Response({
            'message': 'Отчет сгенерирован',
            'report': serializer.data
        })
        
    except ReportTemplate.DoesNotExist:
        return Response(
            {'error': 'Шаблон отчета не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_system_settings(request):
    """Получение всех системных настроек"""
    settings = SystemSetting.objects.all()
    serializer = SystemSettingSerializer(settings, many=True)
    return Response({
        'settings': serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_system_setting(request):
    """Обновление системной настройки"""
    key = request.data.get('key')
    value = request.data.get('value')
    
    try:
        setting = SystemSetting.objects.get(key=key)
        setting.value = value
        setting.save()
        
        serializer = SystemSettingSerializer(setting)
        return Response({
            'message': 'Настройка обновлена',
            'setting': serializer.data
        })
        
    except SystemSetting.DoesNotExist:
        return Response(
            {'error': 'Настройка не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )