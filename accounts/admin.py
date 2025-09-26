from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'email', 'birth_date', 'phone', 'avatar')
        }),
        (_('Права доступа'), {
            'fields': ('role', 'parent', 'has_studied_language', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email', 'first_name', 'last_name', 'has_studied_language')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')

# Добавим остальные модели (без Customer)
from courses.models import Course, Group, Lesson, Attendance
from payments.models import Payment, Subscription, Invoice
from chat.models import ChatRoom, Message
from notifications.models import Notification
from feedback.models import Feedback
from crm.models import Lead, Deal

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'level', 'duration_hours', 'is_active', 'created_at']
    list_filter = ['level', 'is_active', 'language', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'teacher', 'student_count', 'available_spots', 'start_date', 'is_active']
    list_filter = ['course', 'teacher', 'is_active', 'start_date']
    search_fields = ['title', 'course__title', 'teacher__username']
    filter_horizontal = ['students']
    readonly_fields = ['created_at']
    
    def student_count(self, obj):
        return obj.student_count
    student_count.short_description = 'Количество студентов'
    
    def available_spots(self, obj):
        return obj.available_spots
    available_spots.short_description = 'Свободных мест'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson_type', 'teacher', 'start_time', 'duration_minutes', 'is_completed']
    list_filter = ['lesson_type', 'teacher', 'is_completed', 'start_time']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'duration_minutes']
    date_hierarchy = 'start_time'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'status', 'comment', 'created_at']
    list_filter = ['status', 'lesson__start_time', 'student']
    search_fields = ['student__username', 'lesson__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['student__username', 'student__email', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'amount', 'currency', 'due_date', 'status']
    list_filter = ['status', 'currency', 'due_date']
    search_fields = ['invoice_number', 'student__username']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    date_hierarchy = 'due_date'

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_type', 'created_by', 'participant_count', 'is_active', 'created_at']
    list_filter = ['chat_type', 'is_active', 'created_at']
    search_fields = ['name', 'participants__username']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'short_content', 'created_at']
    list_filter = ['message_type', 'created_at', 'room']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'sent_at', 'read_at']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'feedback_type', 'rating', 'status', 'created_at']
    list_filter = ['feedback_type', 'status', 'rating', 'created_at']
    search_fields = ['title', 'content', 'student__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'status', 'source', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'lead', 'value', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'lead__first_name', 'lead__last_name']
    readonly_fields = ['created_at', 'updated_at']