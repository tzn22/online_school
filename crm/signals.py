from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from accounts.models import User, StudentProfile, TeacherProfile  # ← Исправлено: импортируем из accounts
from courses.models import Course, Group, Lesson, Attendance
from payments.models import Payment
from .models import Lead, StudentActivity, SupportTicket, TicketMessage  # ← Импортируем только модели CRM

@receiver(post_save, sender=Lead)
def notify_lead_created(sender, instance, created, **kwargs):
    """Уведомление о создании лида"""
    if created:
        # Отправляем уведомление администраторам
        admin_users = User.objects.filter(role='admin')
        for admin in admin_users:
            if admin.email:
                try:
                    subject = f'Новый лид: {instance.first_name} {instance.last_name}'
                    message = f'''
                    Здравствуйте, {admin.get_full_name() or admin.username}!
                    
                    Получен новый лид:
                    Имя: {instance.first_name} {instance.last_name}
                    Email: {instance.email}
                    Телефон: {instance.phone or 'Не указан'}
                    Интересующий курс: {instance.interested_course.title if instance.interested_course else 'Не указан'}
                    Статус: {instance.get_status_display()}
                    Источник: {instance.get_source_display()}
                    
                    Пожалуйста, свяжитесь с клиентом в ближайшее время.
                    
                    С уважением,
                    Онлайн-школа
                    '''
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [admin.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Ошибка отправки email: {e}")

@receiver(post_save, sender=StudentActivity)
def notify_student_activity(sender, instance, created, **kwargs):
    """Уведомление о активности студента"""
    if created:
        student = instance.student
        
        # Отправляем уведомление родителям
        if student.parent and student.parent.email:
            try:
                subject = f'Активность студента: {student.get_full_name()}'
                message = f'''
                Здравствуйте, {student.parent.get_full_name() or student.parent.username}!
                
                Ваш ребенок {student.get_full_name()} выполнил активность:
                Тип: {instance.get_activity_type_display()}
                Описание: {instance.description}
                Дата: {instance.created_at.strftime('%d.%m.%Y %H:%M')}
                
                С уважением,
                Онлайн-школа
                '''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student.parent.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка отправки email родителю: {e}")

@receiver(post_save, sender=SupportTicket)
def notify_support_ticket_created(sender, instance, created, **kwargs):
    """Уведомление о создании тикета поддержки"""
    if created:
        user = instance.user
        
        # Отправляем уведомление администраторам
        admin_users = User.objects.filter(role='admin')
        for admin in admin_users:
            if admin.email:
                try:
                    subject = f'Новый тикет поддержки: {instance.title}'
                    message = f'''
                    Здравствуйте, {admin.get_full_name() or admin.username}!
                    
                    Получен новый тикет поддержки:
                    Пользователь: {user.get_full_name() or user.username}
                    Тема: {instance.title}
                    Описание: {instance.description}
                    Статус: {instance.get_status_display()}
                    Приоритет: {instance.get_priority_display()}
                    Дата: {instance.created_at.strftime('%d.%m.%Y %H:%M')}
                    
                    Пожалуйста, рассмотрите тикет в ближайшее время.
                    
                    С уважением,
                    Служба поддержки
                    '''
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [admin.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Ошибка отправки email админу: {e}")

@receiver(post_save, sender=TicketMessage)
def notify_ticket_message(sender, instance, created, **kwargs):
    """Уведомление о новом сообщении в тикете"""
    if created:
        ticket = instance.ticket
        sender_user = instance.sender
        
        # Определяем получателей
        recipients = []
        
        # Добавляем пользователя тикета (если это не он сам)
        if ticket.user != sender_user and ticket.user.email:
            recipients.append(ticket.user)
        
        # Добавляем назначенного администратора (если это не он сам)
        if ticket.assigned_to and ticket.assigned_to != sender_user and ticket.assigned_to.email:
            recipients.append(ticket.assigned_to)
        
        # Отправляем уведомления
        for recipient in recipients:
            try:
                subject = f'Новое сообщение в тикете: {ticket.title}'
                message = f'''
                Здравствуйте, {recipient.get_full_name() or recipient.username}!
                
                {sender_user.get_full_name() or sender_user.username} отправил новое сообщение в тикет "{ticket.title}":
                "{instance.content[:100]}{'...' if len(instance.content) > 100 else ''}"
                
                Перейдите в тикет, чтобы ответить.
                
                С уважением,
                Служба поддержки
                '''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка отправки email: {e}")