from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Test, Question, Student, Attempt, Answer
from .forms import StudentRegistrationForm, TestForm, QuestionForm
import json


def test_list(request):
    """Список активных тестов"""
    tests = Test.objects.filter(is_active=True)
    context = {'tests': tests}
    return render(request, 'test_list.html', context)


def test_detail(request, access_link):
    """Детали теста и регистрация студента"""
    test = get_object_or_404(Test, access_link=access_link)

    if not test.is_available():
        messages.error(request, 'Тест недоступен в данный момент')
        return redirect('test_list')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student, created = Student.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'name': form.cleaned_data['name'],
                    'telegram': form.cleaned_data.get('telegram', ''),
                    'institution': form.cleaned_data.get('institution', ''),
                    'specialization': form.cleaned_data.get('specialization', ''),
                }
            )

            # Создаем новую попытку
            attempt = Attempt.objects.create(test=test, student=student)
            return redirect('take_test', attempt_id=attempt.id)
    else:
        form = StudentRegistrationForm()

    context = {
        'test': test,
        'form': form,
    }
    return render(request, 'test_detail.html', context)


def take_test(request, attempt_id):
    """Прохождение теста"""
    attempt = get_object_or_404(Attempt, id=attempt_id)

    # Проверка, что тест еще не завершен
    if attempt.end_time:
        return redirect('test_result', attempt_id=attempt.id)

    questions = attempt.test.questions.all().order_by('order_number')

    if request.method == 'POST':
        # Обработка ответов
        for question in questions:
            field_name = f'question_{question.id}'

            if question.question_type == 'single_choice':
                answer_data = {'answer': request.POST.get(field_name)}

            elif question.question_type == 'multiple_choice':
                answer_data = {'answers': request.POST.getlist(field_name)}

            elif question.question_type in ['text_input', 'number_input']:
                answer_data = {'answer': request.POST.get(field_name, '')}

            elif question.question_type == 'matching':
                pairs = {}
                for key in request.POST:
                    if key.startswith(f'match_{question.id}_'):
                        item_id = key.split('_')[-1]
                        pairs[item_id] = request.POST.get(key)
                answer_data = {'pairs': pairs}

            elif question.question_type == 'ordering':
                order = request.POST.getlist(f'order_{question.id}')
                answer_data = {'order': order}

            # Создаем и проверяем ответ
            answer = Answer.objects.create(
                attempt=attempt,
                question=question,
                student_answer=answer_data
            )
            answer.check_answer()

        # Подсчитываем результат
        attempt.calculate_score()

        return redirect('test_result', attempt_id=attempt.id)

    context = {
        'attempt': attempt,
        'test': attempt.test,
        'questions': questions,
    }
    return render(request, 'take_test.html', context)


def test_result(request, attempt_id):
    """Результаты теста"""
    attempt = get_object_or_404(Attempt, id=attempt_id)

    # Получаем все ответы с вопросами
    answers = attempt.answers.select_related('question').all()
    answers_list = []
    for answer in answers:
        answers_list.append(answer)
    print(answers_list)

    context = {
        'attempt': attempt,
        'test': attempt.test,
        'student': attempt.student,
        'answers': answers_list,
    }
    return render(request, 'result.html', context)


# Административные представления
@login_required
def create_test(request):
    """Создание теста"""
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.creator = request.user
            test.save()
            messages.success(request, 'Тест успешно создан')
            return redirect('add_questions', test_id=test.id)
    else:
        form = TestForm()

    return render(request, 'admin/test_form.html', {'form': form})


@login_required
def add_questions(request, test_id):
    """Добавление вопросов к тесту"""
    test = get_object_or_404(Test, id=test_id, creator=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, 'Вопрос добавлен')
            return redirect('add_questions', test_id=test.id)
    else:
        form = QuestionForm()

    questions = test.questions.all()
    context = {
        'test': test,
        'form': form,
        'questions': questions,
    }
    return render(request, 'admin/question_form.html', context)


@login_required
def test_statistics(request, test_id):
    """Статистика по тесту"""
    test = get_object_or_404(Test, id=test_id, creator=request.user)
    attempts = test.attempts.filter(end_time__isnull=False).select_related('student')

    total_attempts = attempts.count()
    passed_attempts = attempts.filter(passed=True).count()
    avg_score = attempts.aggregate(models.Avg('score'))['score__avg'] or 0

    context = {
        'test': test,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'admin/test_statistics.html', context)
