# Инструкция по развертыванию

## Быстрый старт

1. Распакуйте архив проекта
2. Перейдите в директорию проекта:
   ```bash
   cd internship_testing
   ```

3. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   ```

4. Активируйте виртуальное окружение:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

5. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

6. Создайте файл .env (скопируйте из .env.example):
   ```bash
   cp .env .env
   ```

7. Примените миграции:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

8. Создайте суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

9. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```

10. Откройте в браузере: http://127.0.0.1:8000/

## Первые шаги после установки

1. Войдите в админ-панель: http://127.0.0.1:8000/admin/
2. Создайте первый тест
3. Добавьте вопросы к тесту
4. Скопируйте ссылку на тест (access_link)
5. Пройдите тест как студент

## Создание тестового теста (через Django shell)

```bash
python manage.py shell
```

```python
from testing.models import User, Test, Question
from django.utils import timezone
from datetime import timedelta

# Создайте пользователя-организатора
user = User.objects.create_user(
    username='teacher',
    email='teacher@example.com',
    password='password123',
    role='teacher'
)

# Создайте тест
test = Test.objects.create(
    creator=user,
    title='Тест по программированию',
    description='Базовые вопросы по Python',
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=30),
    passing_threshold=70.0,
    is_active=True
)

# Добавьте вопросы
Question.objects.create(
    test=test,
    question_text='Какой тип данных используется для хранения целых чисел в Python?',
    question_type='single_choice',
    points=1,
    order_number=1,
    options={'options': [
        {'id': 1, 'text': 'int'},
        {'id': 2, 'text': 'float'},
        {'id': 3, 'text': 'string'},
        {'id': 4, 'text': 'bool'}
    ]},
    correct_answer={'answer': 1}
)

print(f"Тест создан! Ссылка: {test.access_link}")
```
