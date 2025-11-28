from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Test, Question, Student, Attempt, Answer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'created_at']
    list_filter = ['role', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role',)}),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'start_date', 'end_date', 'is_active', 'access_link']
    list_filter = ['is_active', 'start_date', 'notification_type']
    search_fields = ['title', 'description']
    readonly_fields = ['access_link', 'created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('creator', 'title', 'description', 'access_link')
        }),
        ('Настройки теста', {
            'fields': ('start_date', 'end_date', 'passing_threshold', 'is_active', 'notification_type')
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'question_text', 'question_type', 'test', 'points']
    list_filter = ['question_type', 'test']
    search_fields = ['question_text']
    ordering = ['test', 'order_number']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'telegram', 'institution', 'created_at']
    search_fields = ['name', 'email', 'institution']
    list_filter = ['institution', 'specialization']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'start_time', 'score', 'passed', 'result_sent']
    list_filter = ['passed', 'result_sent', 'test']
    search_fields = ['student__name', 'student__email']
    readonly_fields = ['start_time', 'end_time', 'score', 'passed']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct', 'question__question_type']
    readonly_fields = ['is_correct', 'points_earned']
