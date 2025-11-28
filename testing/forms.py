from django import forms
from .models import Test, Question, Student


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


class QuestionForm(forms.ModelForm):
    """Форма создания/редактирования вопроса"""

    # Дополнительные поля для разных типов вопросов
    option_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    option_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    option_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    option_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    correct_option = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    correct_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

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
                    options.append({'id': i, 'text': option_text})
            question.options = {'options': options}

            if question.question_type == 'single_choice':
                correct_opt = self.cleaned_data.get('correct_option', 1)
                question.correct_answer = {'answer': correct_opt}

        elif question.question_type in ['text_input', 'number_input']:
            correct_text = self.cleaned_data.get('correct_text', '')
            question.correct_answer = {'answer': correct_text}
            question.options = {}

        if commit:
            question.save()
        return question
