from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from datetime import datetime, timedelta

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
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Customer(models.Model):
    """Клиент CRM"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        null=True,
        blank=True,
        verbose_name=_('Пользователь системы')
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Компания')
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Должность')
    )
    lead = models.OneToOneField(
        Lead,  # ← Используем напрямую, без импорта
        on_delete=models.CASCADE,
        related_name='customer',
        null=True,
        blank=True,
        verbose_name=_('Лид')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_customers',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Назначен менеджеру')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    last_contacted = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Последний контакт')
    )
    
    class Meta:
        verbose_name = _('Клиент')
        verbose_name_plural = _('Клиенты')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['lead', 'created_at']),
            models.Index(fields=['assigned_to', 'created_at']),
            models.Index(fields=['company']),
            models.Index(fields=['position']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name() or self.user.username} ({self.company})"
        elif self.lead:
            return f"{self.lead.first_name} {self.lead.last_name} ({self.company})"
        return f"Клиент {self.id}"

class Deal(models.Model):
    """Сделка CRM"""
    DEAL_STATUS_CHOICES = [
        ('new', _('Новая')),
        ('qualified', _('Квалифицирована')),
        ('proposal', _('Предложение отправлено')),
        ('negotiation', _('Переговоры')),
        ('won', _('Выиграна')),
        ('lost', _('Проиграна')),
        ('cancelled', _('Отменена')),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название сделки')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name=_('Клиент')
    )
    lead = models.ForeignKey(
        Lead,  # ← Используем напрямую, без импорта
        on_delete=models.CASCADE,
        related_name='deals',
        null=True,
        blank=True,
        verbose_name=_('Лид')
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Сумма сделки')
    )
    currency = models.CharField(
        max_length=3,
        default='RUB',
        verbose_name=_('Валюта')
    )
    status = models.CharField(
        max_length=20,
        choices=DEAL_STATUS_CHOICES,
        default='new',
        verbose_name=_('Статус')
    )
    probability = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Вероятность (%)')
    )
    expected_close_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Ожидаемая дата закрытия')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deals',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Назначен менеджеру')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_deals',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата закрытия')
    )
    
    class Meta:
        verbose_name = _('Сделка')
        verbose_name_plural = _('Сделки')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['lead', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_to', 'created_at']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_won(self):
        return self.status == 'won'
    
    @property
    def is_lost(self):
        return self.status == 'lost'
    
    @property
    def is_closed(self):
        return self.status in ['won', 'lost', 'cancelled']

class Activity(models.Model):
    """Активность CRM"""
    ACTIVITY_TYPE_CHOICES = [
        ('call', _('Звонок')),
        ('meeting', _('Встреча')),
        ('email', _('Email')),
        ('task', _('Задача')),
        ('note', _('Заметка')),
        ('deal', _('Сделка')),
        ('customer', _('Клиент')),
    ]
    
    ACTIVITY_STATUS_CHOICES = [
        ('planned', _('Запланировано')),
        ('completed', _('Завершено')),
        ('cancelled', _('Отменено')),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название активности')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name=_('Тип активности')
    )
    status = models.CharField(
        max_length=20,
        choices=ACTIVITY_STATUS_CHOICES,
        default='planned',
        verbose_name=_('Статус')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        verbose_name=_('Клиент')
    )
    lead = models.ForeignKey(
        Lead,  # ← Используем напрямую, без импорта
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        verbose_name=_('Лид')
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        verbose_name=_('Сделка')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_activities',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Назначен пользователю')
    )
    due_date = models.DateTimeField(
        verbose_name=_('Срок выполнения')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_activities',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Активность')
        verbose_name_plural = _('Активности')
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['assigned_to', 'due_date']),
            models.Index(fields=['customer', 'due_date']),
            models.Index(fields=['lead', 'due_date']),
            models.Index(fields=['deal', 'due_date']),
            models.Index(fields=['activity_type', 'status']),
            models.Index(fields=['status', 'due_date']),
        ]
    
    def __str__(self):
        return self.title

class Task(models.Model):
    """Задача CRM"""
    TASK_PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
    ]
    
    TASK_STATUS_CHOICES = [
        ('new', _('Новая')),
        ('in_progress', _('В работе')),
        ('completed', _('Завершена')),
        ('cancelled', _('Отменена')),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название задачи')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    priority = models.CharField(
        max_length=10,
        choices=TASK_PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Приоритет')
    )
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='new',
        verbose_name=_('Статус')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Назначен пользователю')
    )
    due_date = models.DateTimeField(
        verbose_name=_('Срок выполнения')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['assigned_to', 'due_date']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return self.title

class Note(models.Model):
    """Заметка CRM"""
    NOTE_TYPE_CHOICES = [
        ('general', _('Общая')),
        ('customer', _('О клиенте')),
        ('deal', _('О сделке')),
        ('lead', _('О лиде')),
        ('activity', _('Об активности')),
        ('internal', _('Внутренняя')),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название заметки')
    )
    content = models.TextField(
        verbose_name=_('Содержание')
    )
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default='general',
        verbose_name=_('Тип заметки')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True,
        verbose_name=_('Клиент')
    )
    lead = models.ForeignKey(
        Lead,  # ← Используем напрямую, без импорта
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True,
        verbose_name=_('Лид')
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True,
        verbose_name=_('Сделка')
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True,
        verbose_name=_('Активность')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_notes',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Приватная заметка')
    )
    
    class Meta:
        verbose_name = _('Заметка')
        verbose_name_plural = _('Заметки')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['lead', 'created_at']),
            models.Index(fields=['deal', 'created_at']),
            models.Index(fields=['activity', 'created_at']),
            models.Index(fields=['note_type', 'created_at']),
            models.Index(fields=['is_private', 'created_at']),
        ]
    
    def __str__(self):
        return self.title

class Report(models.Model):
    """Отчет CRM"""
    REPORT_TYPE_CHOICES = [
        ('sales', _('Продажи')),
        ('leads', _('Лиды')),
        ('customers', _('Клиенты')),
        ('activities', _('Активности')),
        ('tasks', _('Задачи')),
        ('performance', _('Производительность')),
        ('financial', _('Финансовый')),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название отчета')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name=_('Тип отчета')
    )
    period_start = models.DateField(
        verbose_name=_('Начало периода')
    )
    period_end = models.DateField(
        verbose_name=_('Конец периода')
    )
    data = models.JSONField(
        default=dict,
        verbose_name=_('Данные отчета')
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        limit_choices_to={'role': 'admin'},
        verbose_name=_('Сгенерирован пользователем')
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата генерации')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Опубликован')
    )
    file = models.FileField(
        upload_to='crm_reports/',
        blank=True,
        null=True,
        verbose_name=_('Файл отчета')
    )
    file_size = models.BigIntegerField(
        default=0,
        verbose_name=_('Размер файла (байты)')
    )
    
    class Meta:
        verbose_name = _('Отчет')
        verbose_name_plural = _('Отчеты')
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'generated_at']),
            models.Index(fields=['generated_by', 'generated_at']),
            models.Index(fields=['is_published', 'generated_at']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return self.title