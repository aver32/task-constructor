from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'testing'

urlpatterns = [
    # Публичные URL
    path('', views.test_list, name='test_list'),
    path('test/<str:access_link>/', views.test_detail, name='test_detail'),
    path('attempt/<int:attempt_id>/take/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/result/', views.test_result, name='test_result'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='testing:test_list'), name='logout'),
    path('teacher/register/', views.teacher_register, name='teacher_register'),

    # Преподавательская панель
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/tests/', views.teacher_tests, name='teacher_tests'),
    path('teacher/test/create/', views.create_test, name='create_test'),
    path('teacher/test/<int:test_id>/edit/', views.edit_test, name='edit_test'),
    path('teacher/test/<int:test_id>/questions/', views.add_questions, name='add_questions'),
    path('teacher/test/<int:test_id>/statistics/', views.test_statistics, name='test_statistics'),
    path('teacher/test/<int:test_id>/attempts/', views.test_attempts, name='test_attempts'),
    path('teacher/attempt/<int:attempt_id>/', views.attempt_detail, name='attempt_detail'),
]
