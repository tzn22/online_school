from django.contrib import admin
from .models import Course, Group, Lesson, Attendance

# Удаляем все существующие регистрации моделей
try:
    admin.site.unregister(Course)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Lesson)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Attendance)
except admin.sites.NotRegistered:
    pass

# Регистрируем модели заново
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
