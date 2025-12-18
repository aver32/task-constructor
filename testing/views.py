from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied

from .models import Test, Question, Student, Attempt, Answer, User
from .forms import StudentRegistrationForm, TestForm, QuestionForm, TeacherRegistrationForm
import json

# --- Утилиты ---
def teacher_required(view_func):
    """Декоратор: доступ только для пользователей с ролью teacher или admin."""
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('testing:login')
        if request.user.role not in ('teacher', 'admin'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped


# ---------- Публичные view (как было) ----------
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
        return redirect('testing:test_list')

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
            # Сохраняем идентификатор email в сессии для защиты от чужих попыток (опционально)
            request.session['last_attempt_student_email'] = student.email
            return redirect('testing:take_test', attempt_id=attempt.id)
    else:
        form = StudentRegistrationForm()

    context = {
        'test': test,
        'form': form,
    }
    return render(request, 'test_detail.html', context)


def take_test(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)

    if attempt.end_time:
        return redirect('testing:test_result', attempt_id=attempt.id)

    if 'last_attempt_student_email' in request.session:
        if request.session['last_attempt_student_email'] != attempt.student.email:
            return HttpResponseForbidden('Эта попытка не для текущего пользователя сессии.')

    questions = attempt.test.questions.all().order_by('order_number')

    if request.method == 'POST':

        for question in questions:
            field_name = f'question_{question.id}'

            # ----- ОДИН ВЫБОР -----
            if question.question_type == 'single_choice':
                answer_data = {'answer': request.POST.get(field_name)}

            # ----- МНОЖЕСТВЕННЫЙ -----
            elif question.question_type == 'multiple_choice':
                answer_data = {'answers': request.POST.getlist(field_name)}

            # ----- ТЕКСТ / ЧИСЛО -----
            elif question.question_type in ['text_input', 'number_input']:
                answer_data = {'answer': request.POST.get(field_name, '')}

            # ----- НОВЫЙ ТИП: СООТНЕСЕНИЕ -----
            elif question.question_type == 'matching':
                pairs = {}
                for left in question.options.get('left_items', []):
                    left_id = left['id']
                    key = f"match_{question.id}_{left_id}"
                    pairs[left_id] = request.POST.get(key, '').strip().upper()
                answer_data = {'pairs': pairs}

            # ----- УПОРЯДОЧИВАНИЕ (если будет) -----
            elif question.question_type == 'ordering':
                order = request.POST.getlist(f'order_{question.id}')
                answer_data = {'order': order}

            else:
                answer_data = {'answer': request.POST.get(field_name, '')}

            answer = Answer.objects.create(
                attempt=attempt,
                question=question,
                student_answer=answer_data
            )
            answer.check_answer()

        attempt.calculate_score()
        return redirect('testing:test_result', attempt_id=attempt.id)

    return render(request, 'take_test.html', {
        'attempt': attempt,
        'test': attempt.test,
        'questions': questions,
    })



def test_result(request, attempt_id):
    """Результаты теста"""
    attempt = get_object_or_404(Attempt, id=attempt_id)

    # Получаем все ответы с вопросами
    answers = attempt.answers.select_related('question').all()
    answers_list = []
    for answer in answers:
        answers_list.append(answer)

    context = {
        'attempt': attempt,
        'test': attempt.test,
        'student': attempt.student,
        'answers': answers_list,
    }
    return render(request, 'result.html', context)


# ---------- Преподавательские представления ----------
def teacher_register(request):
    """Регистрация преподавателя (создаёт User с ролью teacher)."""
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна. Добро пожаловать!')
            return redirect('testing:teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'teacher/register.html', {'form': form})


@login_required
@teacher_required
def teacher_dashboard(request):
    """Преподавательская панель (обзор)."""
    tests_count = Test.objects.filter(creator=request.user).count()
    attempts_count = Attempt.objects.filter(test__creator=request.user, end_time__isnull=False).count()
    context = {
        'tests_count': tests_count,
        'attempts_count': attempts_count,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@teacher_required
def teacher_tests(request):
    """Список тестов текущего преподавателя."""
    tests = Test.objects.filter(creator=request.user).order_by('-created_at')
    return render(request, 'teacher/tests_list.html', {'tests': tests})


@login_required
@teacher_required
def create_test(request):
    """Создание теста — только для преподавателей."""
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.creator = request.user
            test.save()
            messages.success(request, 'Тест успешно создан')
            return redirect('testing:add_questions', test_id=test.id)
    else:
        form = TestForm()
    return render(request, 'admin/test_form.html', {'form': form, 'is_edit': False})


@login_required
@teacher_required
def edit_test(request, test_id):
    """Редактирование теста — только автор может редактировать."""
    test = get_object_or_404(Test, id=test_id, creator=request.user)

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тест обновлён')
            return redirect('testing:teacher_tests')
    else:
        form = TestForm(instance=test)

    return render(request, 'admin/test_form.html', {'form': form, 'is_edit': True, 'test': test})


@login_required
@teacher_required
def add_questions(request, test_id):
    """Добавление вопросов к тесту — только автор теста."""
    test = get_object_or_404(Test, id=test_id, creator=request.user)
    questions = test.questions.all()

    # Вычисляем следующий номер вопроса для отображения
    next_order = questions.count() + 1

    if request.method == 'POST':
        form = QuestionForm(request.POST, test=test)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, 'Вопрос добавлен')
            return redirect('testing:add_questions', test_id=test.id)
    else:
        form = QuestionForm(test=test)

    context = {
        'test': test,
        'form': form,
        'questions': questions,
        'next_order': next_order,
    }
    return render(request, 'admin/question_form.html', context)


@login_required
@teacher_required
def test_statistics(request, test_id):
    """Статистика по тесту (как раньше) — доступен автору."""
    test = get_object_or_404(Test, id=test_id, creator=request.user)
    attempts = test.attempts.filter(end_time__isnull=False).select_related('student')

    total_attempts = attempts.count()
    passed_attempts = attempts.filter(passed=True).count()
    from django.db import models as dj_models
    avg_score = attempts.aggregate(dj_models.Avg('score'))['score__avg'] or 0

    context = {
        'test': test,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'admin/test_statistics.html', context)


@login_required
@teacher_required
def test_attempts(request, test_id):
    """Список завершённых попыток по тесту (только автор)."""
    test = get_object_or_404(Test, id=test_id, creator=request.user)
    attempts = test.attempts.filter(end_time__isnull=False).select_related('student').order_by('-end_time')
    return render(request, 'teacher/test_attempts.html', {'test': test, 'attempts': attempts})


@login_required
@teacher_required
def attempt_detail(request, attempt_id):
    """Детальный просмотр конкретной попытки (вопрос/ответ/очки)."""
    attempt = get_object_or_404(Attempt, id=attempt_id, test__creator=request.user)
    answers = attempt.answers.select_related('question').all()
    for answer in answers:
        options = answer.question.options
        if options:
            list_results = []
            options_answers = options.get('options', {})
            student_answer_index = answer.student_answer.get('answer', '')
            student_answer_indices = answer.student_answer.get('answers', [])
            for index in student_answer_indices:
                list_results.append(options_answers[int(index) - 1].get('text', ''))
            result = ', '.join(list_results)
            if student_answer_index:
                result = options_answers[int(student_answer_index) - 1].get('text', '')
            answer.student_answer = result
        else:
            answer.student_answer = answer.student_answer.get('answer', '')
    return render(request, 'teacher/attempt_detail.html', {
        'attempt': attempt,
        'answers': answers,
    })
