from django import forms
from django.db import models

from .models import Test, Question, Student, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class StudentRegistrationForm(forms.Form):
    """Форма регистрации студента для прохождения теста"""
    name = forms.CharField(
        max_length=255,
        label='Имя и фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван Иванов'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    telegram = forms.CharField(
        max_length=100,
        required=False,
        label='Telegram (опционально)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
    )
    institution = forms.CharField(
        max_length=255,
        required=False,
        label='Учебное заведение',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'МГУ'})
    )
    specialization = forms.CharField(
        max_length=255,
        required=False,
        label='Специализация',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Информатика'})
    )


class TestForm(forms.ModelForm):
    """Форма создания/редактирования теста"""

    notification_type = forms.MultipleChoiceField(
        choices=Test.NOTIFICATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Типы уведомлений'
    )

    class Meta:
        model = Test
        fields = ['title', 'description', 'start_date', 'end_date',
                  'passing_threshold', 'is_active', 'notification_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'passing_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionForm(forms.ModelForm):
    """Форма создания/редактирования вопроса"""

    # Поле для указания количества вариантов
    num_options = forms.IntegerField(
        required=False,
        initial=4,
        min_value=2,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'num_options'}),
        label="Количество вариантов ответа"
    )
    num_matrix_rows = forms.IntegerField(
        required=False,
        initial=3,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'num_matrix_rows'}),
        label="Количество строк (утверждений)"
    )

    num_matrix_cols = forms.IntegerField(
        required=False,
        initial=4,
        min_value=2,
        max_value=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'num_matrix_cols'}),
        label="Количество столбцов (вариантов)"
    )
    matrix_row_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label="Строка 1")
    matrix_row_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label="Строка 2")
    matrix_row_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label="Строка 3")
    matrix_row_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label="Строка 4")
    matrix_row_5 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label="Строка 5")

    # Колонки матрицы (верхняя часть - варианты ответов)
    matrix_col_A = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="A")
    matrix_col_B = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Б")
    matrix_col_C = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="В")
    matrix_col_D = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Г")
    matrix_col_E = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Д")
    matrix_col_F = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Е")

    # Правильные ответы для каждой строки (какая колонка правильная)
    matrix_answer_placeholder = 'A, Б, В, Г, Д или Е'
    matrix_answer_1 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'A, Б, В, Г, Д или Е'}), label="Ответ для строки 1")
    matrix_answer_2 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'A, Б, В, Г, Д или Е'}), label="Ответ для строки 2")
    matrix_answer_3 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'A, Б, В, Г, Д или Е'}), label="Ответ для строки 3")
    matrix_answer_4 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'A, Б, В, Г, Д или Е'}), label="Ответ для строки 4")
    matrix_answer_5 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'A, Б, В, Г, Д или Е'}), label="Ответ для строки 5")

    # Динамические поля для вариантов (создадим их динамически)
    option_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 1")
    option_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 2")
    option_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 3")
    option_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 4")
    option_5 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 5")
    option_6 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 6")
    option_7 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 7")
    option_8 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 8")
    option_9 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                               label="Вариант 9")
    option_10 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control option-field'}),
                                label="Вариант 10")

    # Чекбоксы для отметки правильных ответов
    correct_1 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_2 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_3 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_4 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_5 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_6 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_7 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_8 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_9 = forms.BooleanField(required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                   label="")
    correct_10 = forms.BooleanField(required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input correct-checkbox'}),
                                    label="")

    correct_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   label='Правильный текст')

    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        self.test = kwargs.pop('test', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super().save(commit=False)

        # Автоматически определяем порядковый номер
        if self.test:
            max_order = Question.objects.filter(test=self.test).aggregate(models.Max('order_number'))[
                'order_number__max']
            question.order_number = (max_order or 0) + 1

        # Формируем options и correct_answer в зависимости от типа вопроса
        if question.question_type in ['single_choice', 'multiple_choice']:
            options = []
            correct_answers = []

            # Определяем количество вариантов
            num_options = self.cleaned_data.get('num_options', 4)

            for i in range(1, num_options + 1):
                option_text = self.cleaned_data.get(f'option_{i}')
                if option_text:
                    options.append({'id': str(i), 'text': option_text})

                    # Проверяем, отмечен ли этот вариант как правильный
                    if self.cleaned_data.get(f'correct_{i}'):
                        correct_answers.append(str(i))

            question.options = {'options': options}

            if question.question_type == 'single_choice':
                # Для одиночного выбора берем первый отмеченный ответ
                question.correct_answer = {'answer': correct_answers[0] if correct_answers else ''}
            else:
                # Для множественного выбора сохраняем все отмеченные ответы
                question.correct_answer = {'answers': correct_answers}

        elif question.question_type in ['text_input', 'number_input']:
            correct_text = self.cleaned_data.get('correct_text', '')
            question.correct_answer = {'answer': correct_text}
            question.options = {}

        # ЗАМЕНИТЕ ВЕСЬ БЛОК elif question.question_type == 'matrix':
        elif question.question_type == 'matrix':
            rows = []
            cols = []
            correct_matrix = {}

            # Получаем количество строк и столбцов
            num_rows = self.cleaned_data.get('num_matrix_rows', 3)
            num_cols = self.cleaned_data.get('num_matrix_cols', 4)
            answer_type = self.cleaned_data.get('matrix_answer_type', 'single')  # ДОБАВЛЕНО

            # Собираем строки (row) - только те, которые заполнены
            for i in range(1, 6):  # максимум 5 строк
                if i <= num_rows:
                    row_text = self.cleaned_data.get(f'matrix_row_{i}')
                    if row_text:
                        rows.append({'id': str(i), 'text': row_text})

            # Собираем колонки (column) - только те, которые заполнены
            letters = ['A', 'B', 'C', 'D', 'E', 'F']
            for idx, letter in enumerate(letters):
                if idx < num_cols:
                    col_text = self.cleaned_data.get(f'matrix_col_{letter}')
                    if col_text:
                        cols.append({'id': letter, 'text': col_text})

            # Собираем правильные ответы
            for i in range(1, 6):
                if i <= num_rows:
                    row_text = self.cleaned_data.get(f'matrix_row_{i}')
                    if row_text:
                        answer = self.cleaned_data.get(f'matrix_answer_{i}', '').strip().upper()
                        if answer:
                            if str(i) not in correct_matrix:
                                correct_matrix[str(i)] = {}

                            # ИЗМЕНЕНО: поддержка множественных ответов
                            if answer_type == 'multiple':
                                # Разделяем по запятой и обрабатываем каждый ответ
                                answers = [a.strip() for a in answer.split(',') if a.strip()]
                                for ans in answers:
                                    correct_matrix[str(i)][ans] = True
                            else:
                                # Один ответ
                                correct_matrix[str(i)][answer] = True

            question.options = {
                'rows': rows,
                'cols': cols,
                'answer_type': answer_type  # ДОБАВЛЕНО
            }
            question.correct_answer = {
                'matrix': correct_matrix
            }

        if commit:
            question.save()
        return question


class TeacherRegistrationForm(forms.ModelForm):
    """Регистрация преподавателя (User)"""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают")
        try:
            validate_password(p1)
        except ValidationError as e:
            raise ValidationError(e)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user
