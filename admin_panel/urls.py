from django.urls import path
from .views import (
    AdminActionLogListView,
    ReportTemplateListView,
    ReportTemplateDetailView,
    GeneratedReportListView,
    GeneratedReportDetailView,
    MassEmailCampaignListView,
    MassEmailCampaignDetailView,
    SystemSettingListView,
    SystemSettingDetailView,
    admin_dashboard,
    system_health_check,
    send_mass_email,
    generate_report,
    get_system_settings,
    update_system_setting
)

urlpatterns = [
    # Дашборд и здоровье системы
    path('dashboard/', admin_dashboard, name='admin-dashboard'),
    path('health/', system_health_check, name='system-health-check'),
    
    # Логи действий администраторов
    path('action-logs/', AdminActionLogListView.as_view(), name='admin-action-logs'),
    
    # Шаблоны отчетов
    path('report-templates/', ReportTemplateListView.as_view(), name='report-templates'),
    path('report-templates/<int:pk>/', ReportTemplateDetailView.as_view(), name='report-template-detail'),
    
    # Сгенерированные отчеты
    path('generated-reports/', GeneratedReportListView.as_view(), name='generated-reports'),
    path('generated-reports/<int:pk>/', GeneratedReportDetailView.as_view(), name='generated-report-detail'),
    
    # Email кампании
    path('email-campaigns/', MassEmailCampaignListView.as_view(), name='email-campaigns'),
    path('email-campaigns/<int:pk>/', MassEmailCampaignDetailView.as_view(), name='email-campaign-detail'),
    
    # Системные настройки
    path('system-settings/', SystemSettingListView.as_view(), name='system-settings'),
    path('system-settings/<int:pk>/', SystemSettingDetailView.as_view(), name='system-setting-detail'),
    
    # Действия
    path('send-mass-email/', send_mass_email, name='send-mass-email'),
    path('generate-report/', generate_report, name='generate-report'),
    path('system-settings/all/', get_system_settings, name='get-system-settings'),
    path('system-settings/update/', update_system_setting, name='update-system-setting'),
]