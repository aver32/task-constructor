from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('testing.urls')),
]

admin.site.site_header = 'Система тестирования стажёров'
admin.site.site_title = 'Админ-панель'
admin.site.index_title = 'Управление тестами'
