from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json
import uuid


class User(AbstractUser):
    """Пользователи системы (организаторы)"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Test(models.Model):
    """Тесты для стажировки"""
    NOTIFICATION_CHOICES = [
        ('account', 'Личный кабинет'),
        ('email', 'Email'),
        ('telegram', 'Telegram'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    title = models.CharField(max_length=255, verbose_name='Название теста')
    description = models.TextField(verbose_name='Описание теста')
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    passing_threshold = models.FloatField(verbose_name='Проходной балл (%)', default=70.0)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    access_link = models.CharField(max_length=255, unique=True, blank=True)
    notification_type = models.JSONField(
        verbose_name='Типы уведомлений',
        default=list,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.access_link:
            self.access_link = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def is_available(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def get_total_points(self):
        return sum(q.points for q in self.questions.all())

    class Meta:
        db_table = 'tests'
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """Вопросы теста"""
    QUESTION_TYPES = [
        ('single_choice', 'Один вариант ответа'),
        ('multiple_choice', 'Множественный выбор'),
        ('text_input', 'Ввод текста'),
        ('number_input', 'Ввод числа'),
        ('matching', 'Соотнесение'),
        ('ordering', 'Упорядочивание'),
        ('matrix', 'Матричный вопрос'),  # НОВЫЙ ТИП
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(verbose_name='Текст вопроса')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    points = models.IntegerField(default=1, verbose_name='Баллы за вопрос')
    options = models.JSONField(default=dict, verbose_name='Варианты ответов')
    correct_answer = models.JSONField(default=dict, verbose_name='Правильный ответ')
    order_number = models.IntegerField(default=0, verbose_name='Порядковый номер')

    class Meta:
        db_table = 'questions'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order_number']

    def __str__(self):
        return f"{self.order_number}. {self.question_text[:50]}"


class Student(models.Model):
    """Студенты, проходящие тесты"""
    name = models.CharField(max_length=255, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram')
    institution = models.CharField(max_length=255, blank=True, verbose_name='Учебное заведение')
    specialization = models.CharField(max_length=255, blank=True, verbose_name='Специализация')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Attempt(models.Model):
    """Попытки прохождения тестов"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0, verbose_name='Набранный балл')
    passed = models.BooleanField(default=False, verbose_name='Пройден')
    result_sent = models.BooleanField(default=False, verbose_name='Результат отправлен')

    class Meta:
        db_table = 'attempts'
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student.name} - {self.test.title} - {self.start_time}"

    def calculate_score(self):
        """Подсчет результата"""
        total_points = 0
        earned_points = 0

        for answer in self.answers.all():
            total_points += answer.question.points
            earned_points += answer.points_earned

        if total_points > 0:
            self.score = (earned_points / total_points) * 100
            self.passed = self.score >= self.test.passing_threshold
        else:
            self.score = 0
            self.passed = False

        self.end_time = timezone.now()
        self.save()


class Answer(models.Model):
    """Ответы студентов на вопросы"""
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    student_answer = models.JSONField(default=dict, verbose_name='Ответ студента')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный')
    points_earned = models.FloatField(default=0.0, verbose_name='Заработанные баллы')

    class Meta:
        db_table = 'answers'
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def check_answer(self):
        """Проверка правильности ответа"""
        question = self.question
        correct = question.correct_answer
        student = self.student_answer

        if question.question_type == 'single_choice':
            student_answer = str(student.get('answer'))
            correct_answer = str(correct.get('answer'))
            self.is_correct = student_answer == correct_answer

        elif question.question_type == 'multiple_choice':
            student_list = [str(v) for v in student.get('answers', [])]
            correct_list = [str(v) for v in correct.get('answers', [])]
            self.is_correct = set(student_list) == set(correct_list)

        elif question.question_type in ['text_input', 'number_input']:
            student_ans = str(student.get('answer', '')).strip().lower()
            correct_ans = str(correct.get('answer', '')).strip().lower()
            self.is_correct = student_ans == correct_ans

        elif question.question_type == 'matching':
            self.is_correct = student.get('pairs') == correct.get('pairs')

        elif question.question_type == 'ordering':
            self.is_correct = student.get('order') == correct.get('order')

        elif question.question_type == 'matrix':
            # Проверка матричного ответа
            student_matrix = student.get('matrix', {})
            correct_matrix = correct.get('matrix', {})

            # Подсчет правильных ответов
            total_cells = 0
            correct_cells = 0

            for row_id in correct_matrix.keys():
                for col_id in correct_matrix[row_id].keys():
                    total_cells += 1
                    student_value = student_matrix.get(row_id, {}).get(col_id)
                    correct_value = correct_matrix[row_id][col_id]

                    if student_value == correct_value:
                        correct_cells += 1

            # Полное совпадение = правильный ответ
            self.is_correct = (total_cells > 0 and correct_cells == total_cells)

            # Частичные баллы за матричные вопросы
            if total_cells > 0:
                self.points_earned = question.points * (correct_cells / total_cells)
            else:
                self.points_earned = 0

            self.save()
            return  # Выходим, чтобы не перезаписать points_earned ниже

        # Начисление баллов для остальных типов
        if self.is_correct:
            self.points_earned = question.points
        else:
            self.points_earned = 0

        self.save()

    def __str__(self):
        return f"Ответ на {self.question.order_number} вопрос"