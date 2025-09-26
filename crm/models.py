from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import datetime, timedelta
from django.db import models

User = settings.AUTH_USER_MODEL

class Lead(models.Model):
    """Потенциальный клиент (лид)"""
    LEAD_STATUS_CHOICES = [
        ('new', _('Новый')),
        ('contacted', _('Связались')),
        ('interested', _('Заинтересован')),
        ('demo_scheduled', _('Назначена демо-встреча')),
        ('demo_completed', _('Демо-встреча проведена')),
        ('proposal_sent', _('Отправлено предложение')),
        ('negotiation', _('Переговоры')),
        ('converted', _('Конвертирован')),
        ('lost', _('Потерян')),
    ]
    
    LEAD_SOURCE_CHOICES = [
        ('website', _('Сайт')),
        ('social_media', _('Социальные сети')),
        ('referral', _('Реферал')),
        ('advertisement', _('Реклама')),
        ('event', _('Мероприятие')),
        ('other', _('Другое')),
    ]
    
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('Имя')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Фамилия')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон')
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Возраст')
    )
    interested_course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Интересующий курс')
    )
    status = models.CharField(
        max_length=20,
        choices=LEAD_STATUS_CHOICES,
        default='new',
        verbose_name=_('Статус')
    )
    source = models.CharField(
        max_length=20,
        choices=LEAD_SOURCE_CHOICES,
        default='website',
        verbose_name=_('Источник')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Заметки')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Назначен менеджер')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата конверсии')
    )
    
    class Meta:
        verbose_name = _('Лид')
        verbose_name_plural = _('Лиды')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['assigned_to', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['interested_course']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"

class StudentActivity(models.Model):
    """Активность студента"""
    ACTIVITY_TYPE_CHOICES = [
        ('login', _('Вход в систему')),
        ('lesson_attended', _('Посетил занятие')),
        ('lesson_missed', _('Пропустил занятие')),
        ('homework_submitted', _('Сдал домашнее задание')),
        ('homework_late', _('Сдал домашнее задание с опозданием')),
        ('payment_made', _('Сделал платеж')),
        ('feedback_given', _('Оставил отзыв')),
        ('support_request', _('Обратился в поддержку')),
        ('course_completed', _('Завершил курс')),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        limit_choices_to={'role': 'student'},
        verbose_name=_('Студент')
    )
    activity_type = models.CharField(
        max_length=30,
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name=_('Тип активности')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('ID связанного объекта')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP адрес')
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('Активность студента')
        verbose_name_plural = _('Активности студентов')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
            models.Index(fields=['related_object_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.get_activity_type_display()}"

class SupportTicket(models.Model):
    """Тикет поддержки"""
    TICKET_STATUS_CHOICES = [
        ('new', _('Новый')),
        ('in_progress', _('В работе')),
        ('resolved', _('Решен')),
        ('closed', _('Закрыт')),
    ]
    
    TICKET_PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name=_('Пользователь')
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Тема')
    )
    description = models.TextField(
        verbose_name=_('Описание проблемы')
    )
    status = models.CharField(
        max_length=20,
        choices=TICKET_STATUS_CHOICES,
        default='new',
        verbose_name=_('Статус')
    )
    priority = models.CharField(
        max_length=10,
        choices=TICKET_PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Приоритет')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_('Назначен администратору')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата решения')
    )
    
    class Meta:
        verbose_name = _('Тикет поддержки')
        verbose_name_plural = _('Тикеты поддержки')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['assigned_to', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['title']),
        ]
    
    def __str__(self):
        return self.title

class TicketMessage(models.Model):
    """Сообщение тикета"""
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Тикет')
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Отправитель')
    )
    content = models.TextField(
        verbose_name=_('Сообщение')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата')
    )
    
    class Meta:
        verbose_name = _('Сообщение тикета')
        verbose_name_plural = _('Сообщения тикетов')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Сообщение от {self.sender} в тикете {self.ticket.title}"