from django.urls import path
from . import views

urlpatterns = [
    # Публичные URL
    path('', views.test_list, name='test_list'),
    path('test/<str:access_link>/', views.test_detail, name='test_detail'),
    path('attempt/<int:attempt_id>/take/', views.take_test, name='take_test'),
    path('attempt/<int:attempt_id>/result/', views.test_result, name='test_result'),

    # Административные URL
    path('admin/create-test/', views.create_test, name='create_test'),
    path('admin/test/<int:test_id>/questions/', views.add_questions, name='add_questions'),
    path('admin/test/<int:test_id>/statistics/', views.test_statistics, name='test_statistics'),
]
