from django.contrib import admin
from .models import Customer, Deal, Activity, Task, Note, Report, Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'status', 'source', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'position', 'lead', 'assigned_to', 'created_at']
    list_filter = ['created_at', 'assigned_to']
    search_fields = ['user__username', 'company', 'position', 'lead__first_name', 'lead__last_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'value', 'currency', 'status', 'probability', 'assigned_to', 'created_at']
    list_filter = ['status', 'currency', 'probability', 'created_at', 'assigned_to']
    search_fields = ['title', 'customer__user__username', 'customer__lead__first_name']
    readonly_fields = ['created_at', 'updated_at', 'closed_at']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_type', 'status', 'customer', 'lead', 'deal', 'assigned_to', 'due_date']
    list_filter = ['activity_type', 'status', 'due_date', 'assigned_to']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'assigned_to', 'due_date', 'completed_at']
    list_filter = ['priority', 'status', 'due_date', 'assigned_to']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_type', 'customer', 'lead', 'deal', 'activity', 'created_by', 'created_at']
    list_filter = ['note_type', 'is_private', 'created_at', 'created_by']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'period_start', 'period_end', 'generated_by', 'generated_at', 'is_published']
    list_filter = ['report_type', 'is_published', 'generated_at', 'generated_by']
    search_fields = ['title', 'description']
    readonly_fields = ['generated_at', 'data']