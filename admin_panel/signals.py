from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import AdminActionLog, SystemSetting, MassEmailCampaign
from accounts.models import User

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_action(sender, instance, created, **kwargs):
    """Логирование действий с пользователями"""
    # Здесь можно добавить логику для определения, кто выполнил действие
    pass

@receiver(post_save, sender=SystemSetting)
def log_system_setting_change(sender, instance, created, **kwargs):
    """Логирование изменений системных настроек"""
    action_type = 'create' if created else 'update'
    description = f"{'Создана' if created else 'Обновлена'} системная настройка: {instance.name}"
    
    # Здесь можно добавить логирование в AdminActionLog
    pass

@receiver(post_delete, sender=SystemSetting)
def log_system_setting_delete(sender, instance, **kwargs):
    """Логирование удаления системных настроек"""
    description = f"Удалена системная настройка: {instance.name}"
    
    # Здесь можно добавить логирование в AdminActionLog
    pass

@receiver(post_save, sender=MassEmailCampaign)
def log_email_campaign_action(sender, instance, created, **kwargs):
    """Логирование действий с email кампаниями"""
    action_type = 'create' if created else 'update'
    description = f"{'Создана' if created else 'Обновлена'} email кампания: {instance.name}"
    
    # Здесь можно добавить логирование в AdminActionLog
    pass

@receiver(post_delete, sender=MassEmailCampaign)
def log_email_campaign_delete(sender, instance, **kwargs):
    """Логирование удаления email кампаний"""
    description = f"Удалена email кампания: {instance.name}"
    
    # Здесь можно добавить логирование в AdminActionLog
    pass

# === СИГНАЛЫ ДЛЯ АВТОМАТИЧЕСКОГО СОЗДАНИЯ НАСТРОЕК ===

@receiver(post_save, sender=User)
def create_default_system_settings(sender, instance, created, **kwargs):
    """Создание настроек по умолчанию для новых пользователей"""
    if created and instance.is_admin:
        # Создаем системные настройки по умолчанию для администраторов
        default_settings = [
            {
                'key': 'notifications_enabled',
                'name': 'Уведомления включены',
                'description': 'Включить системные уведомления',
                'setting_type': 'boolean',
                'value': 'true',
                'is_public': False,
                'category': 'notifications'
            },
            {
                'key': 'email_notifications',
                'name': 'Email уведомления',
                'description': 'Включить email уведомления',
                'setting_type': 'boolean',
                'value': 'true',
                'is_public': False,
                'category': 'notifications'
            },
            {
                'key': 'push_notifications',
                'name': 'Push уведомления',
                'description': 'Включить push уведомления',
                'setting_type': 'boolean',
                'value': 'true',
                'is_public': False,
                'category': 'notifications'
            },
            {
                'key': 'maintenance_mode',
                'name': 'Режим обслуживания',
                'description': 'Включить режим обслуживания',
                'setting_type': 'boolean',
                'value': 'false',
                'is_public': True,
                'category': 'system'
            },
            {
                'key': 'max_students_per_group',
                'name': 'Максимум студентов в группе',
                'description': 'Максимальное количество студентов в одной группе',
                'setting_type': 'integer',
                'value': '10',
                'is_public': False,
                'category': 'courses'
            }
        ]
        
        for setting_data in default_settings:
            SystemSetting.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )