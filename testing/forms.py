from django import forms
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
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название теста',
            'description': 'Описание',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'passing_threshold': 'Проходной балл (%)',
            'is_active': 'Активен',
            'notification_type': 'Тип уведомления',
        }


class QuestionForm(forms.ModelForm):
    """Форма создания/редактирования вопроса"""

    option_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Вариант 1")
    option_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Вариант 2")
    option_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Вариант 3")
    option_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Вариант 4")

    correct_option = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Правильный вариант')
    correct_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Правильный текст')

    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points', 'order_number']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def save(self, commit=True):
        question = super().save(commit=False)

        # Формируем options и correct_answer в зависимости от типа вопроса
        if question.question_type in ['single_choice', 'multiple_choice']:
            options = []
            for i in range(1, 5):
                option_text = self.cleaned_data.get(f'option_{i}')
                if option_text:
                    options.append({'id': str(i), 'text': option_text})
            question.options = {'options': options}

            if question.question_type == 'single_choice':
                correct_opt = self.cleaned_data.get('correct_option') or ''
                question.correct_answer = {'answer': str(correct_opt)}
            else:
                # Для multiple_choice ожидаем список через запятую, либо поле можно расширить
                correct_opt = self.cleaned_data.get('correct_option') or ''
                answers = [s.strip() for s in str(correct_opt).split(',') if s.strip()]
                question.correct_answer = {'answers': answers}

        elif question.question_type in ['text_input', 'number_input']:
            correct_text = self.cleaned_data.get('correct_text', '')
            question.correct_answer = {'answer': correct_text}
            question.options = {}

        # Для matching/ordering — нужно будет доработать UI (здесь оставляем поля для ручного заполнения через JSON)
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
