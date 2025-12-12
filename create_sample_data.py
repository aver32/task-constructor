# Скрипт для создания примера данных
# Запустите: python manage.py shell < create_sample_data.py

from testing.models import User, Test, Question
from django.utils import timezone
from datetime import timedelta

print("Создание примера данных...")

# Создание пользователя-организатора
user, created = User.objects.get_or_create(
    username='organizer',
    defaults={
        'email': 'organizer@example.com',
        'role': 'teacher'
    }
)
if created:
    user.set_password('admin123')
    user.save()
    print(f"✓ Создан пользователь: {user.username}")

# Создание теста
test = Test.objects.create(
    creator=user,
    title='Тестовое задание для стажеров Python Developer',
    description='''
Этот тест проверяет базовые знания Python и понимание основ программирования.
Для прохождения необходимо набрать минимум 70% правильных ответов.
Время прохождения не ограничено.
    ''',
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=90),
    passing_threshold=70.0,
    is_active=True,
    notification_type=list
)

print(f"✓ Создан тест: {test.title}")
print(f"  Ссылка доступа: {test.access_link}")

# Создание вопросов
questions_data = [
    {
        'question_text': 'Какой оператор используется для создания комментария в Python?',
        'question_type': 'single_choice',
        'points': 1,
        'order_number': 1,
        'options': {'options': [
            {'id': 1, 'text': '#'},
            {'id': 2, 'text': '//'},
            {'id': 3, 'text': '/* */'},
            {'id': 4, 'text': '--'}
        ]},
        'correct_answer': {'answer': 1}
    },
    {
        'question_text': 'Выберите все изменяемые (mutable) типы данных в Python:',
        'question_type': 'multiple_choice',
        'points': 2,
        'order_number': 2,
        'options': {'options': [
            {'id': 1, 'text': 'list'},
            {'id': 2, 'text': 'tuple'},
            {'id': 3, 'text': 'dict'},
            {'id': 4, 'text': 'set'}
        ]},
        'correct_answer': {'answers': [1, 3, 4]}
    },
    {
        'question_text': 'Какой результат выполнения: len("Hello")?',
        'question_type': 'number_input',
        'points': 1,
        'order_number': 3,
        'options': {},
        'correct_answer': {'answer': '5'}
    },
    {
        'question_text': 'Какое ключевое слово используется для определения функции в Python?',
        'question_type': 'text_input',
        'points': 1,
        'order_number': 4,
        'options': {},
        'correct_answer': {'answer': 'def'}
    },
]

for q_data in questions_data:
    Question.objects.create(test=test, **q_data)
    print(f"✓ Добавлен вопрос {q_data['order_number']}")

print("\n" + "="*60)
print("Пример данных успешно создан!")
print("="*60)
print(f"\nДля прохождения теста перейдите по ссылке:")
print(f"http://127.0.0.1:8000/test/{test.access_link}/")
print(f"\nДля входа в админ-панель используйте:")
print(f"Логин: organizer")
print(f"Пароль: admin123")
print("="*60)
