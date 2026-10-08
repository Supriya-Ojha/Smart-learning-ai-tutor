import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required


def home(request):
    return render(request, "home.html")


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long!")
            return redirect("register")

        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least 1 uppercase letter!")
            return redirect("register")

        if not re.search(r"[a-z]", password):
            messages.error(request, "Password must contain at least 1 lowercase letter!")
            return redirect("register")

        if not re.search(r"[0-9]", password):
            messages.error(request, "Password must contain at least 1 number!")
            return redirect("register")

        if not re.search(r"[@#$%!^&*]", password):
            messages.error(request, "Password must contain at least 1 special character!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        messages.success(request, "Registration successful!")

        return redirect("login")

    return render(request, "register.html")


def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password!")

        return redirect("login")

    return render(request, "login.html")


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("login")

    from courses.models import Lesson, Progress, QuizResult

    total_lessons = Lesson.objects.count()

    completed_lessons = Progress.objects.filter(
        user=request.user,
        completed=True
    ).count()

    if total_lessons > 0:
        progress_percentage = int(
            (completed_lessons / total_lessons) * 100
        )
    else:
        progress_percentage = 0

    incomplete_lessons = Lesson.objects.exclude(
        id__in=Progress.objects.filter(
            user=request.user,
            completed=True
        ).values_list(
            "lesson_id",
            flat=True
        )
    )

    recommendation_title = "Keep Learning! 🚀"

    recommendation_message = (
        "Start a lesson and continue building your skills."
    )

    recommended_lesson = None

    if incomplete_lessons.exists():

        recommended_lesson = incomplete_lessons.first()

        recommendation_title = "Recommended For You 🎯"

        recommendation_message = (
            "Continue learning with "
            + recommended_lesson.title
            + ". Complete this lesson to improve your progress."
        )

    quiz_results = QuizResult.objects.filter(
        user=request.user
    )

    total_quiz_attempts = quiz_results.count()

    average_score = 0

    if total_quiz_attempts > 0:

        total_percentage = 0

        for result in quiz_results:

            if result.total_questions > 0:

                percentage = (
                    result.score
                    / result.total_questions
                ) * 100

                total_percentage += percentage

        average_score = int(
            total_percentage
            / total_quiz_attempts
        )

    if average_score < 50 and total_quiz_attempts > 0:

        recommendation_title = "Focus On Revision 📚"

        recommendation_message = (
            "Your average quiz score is "
            + str(average_score)
            + "%. Revise your lessons and try the quizzes again."
        )

    elif average_score >= 80:

        recommendation_title = "Excellent Progress! 🌟"

        recommendation_message = (
            "Your average quiz score is "
            + str(average_score)
            + "%. You are doing great! Try an advanced lesson next."
        )

    return render(
        request,
        "dashboard.html",
        {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "recommendation_title": recommendation_title,
            "recommendation_message": recommendation_message,
            "recommended_lesson": recommended_lesson,
            "total_quiz_attempts": total_quiz_attempts,
            "average_score": average_score
        }
    )


def user_logout(request):

    logout(request)

    return redirect("login")


def my_progress(request):

    if not request.user.is_authenticated:
        return redirect("login")

    from courses.models import Lesson, Progress, QuizResult

    total_lessons = Lesson.objects.count()

    completed_lessons = Progress.objects.filter(
        user=request.user,
        completed=True
    ).count()

    if total_lessons > 0:
        progress_percentage = int(
            (completed_lessons / total_lessons) * 100
        )
    else:
        progress_percentage = 0

    completed_progress = Progress.objects.filter(
        user=request.user,
        completed=True
    ).select_related("lesson")

    quiz_results = QuizResult.objects.filter(
        user=request.user
    ).select_related(
        "quiz"
    ).order_by(
        "-attempted_at"
    )

    total_quiz_attempts = quiz_results.count()

    average_score = 0
    best_score = 0

    if total_quiz_attempts > 0:

        total_percentage = 0

        for result in quiz_results:

            if result.total_questions > 0:

                percentage = (
                    result.score
                    / result.total_questions
                ) * 100

                total_percentage += percentage

                if percentage > best_score:
                    best_score = percentage

        average_score = int(
            total_percentage
            / total_quiz_attempts
        )

        best_score = int(best_score)

    if total_quiz_attempts == 0:
        performance_level = "Start Your First Quiz 📝"

    elif average_score < 50:
        performance_level = "Needs Improvement 📚"

    elif average_score < 80:
        performance_level = "Good Performance 👍"

    else:
        performance_level = "Excellent Performance 🏆"

    return render(
        request,
        "progress.html",
        {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "completed_progress": completed_progress,
            "quiz_results": quiz_results,
            "total_quiz_attempts": total_quiz_attempts,
            "average_score": average_score,
            "best_score": best_score,
            "performance_level": performance_level
        }
    )


def my_profile(request):

    if not request.user.is_authenticated:
        return redirect("login")

    from courses.models import Lesson, Progress

    total_lessons = Lesson.objects.count()

    completed_lessons = Progress.objects.filter(
        user=request.user,
        completed=True
    ).count()

    if total_lessons > 0:
        progress_percentage = int(
            (completed_lessons / total_lessons) * 100
        )
    else:
        progress_percentage = 0

    return render(
        request,
        "profile.html",
        {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage
        }
    )


@staff_member_required
def staff_dashboard(request):

    from courses.models import Course, Lesson, Quiz, QuizResult

    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by(
        "username"
    )

    courses = Course.objects.all().order_by(
        "title"
    )

    lessons = Lesson.objects.all().order_by(
        "title"
    )

    quizzes = Quiz.objects.all().order_by(
        "title"
    )

    quiz_attempts = QuizResult.objects.filter(
        user__is_staff=False
    ).select_related(
        "user",
        "quiz"
    ).order_by(
        "-attempted_at"
    )

    total_students = students.count()
    total_courses = courses.count()
    total_lessons = lessons.count()
    total_quizzes = quizzes.count()

    ai_quizzes = Quiz.objects.filter(
        is_ai_generated=True
    ).count()

    total_quiz_attempts = quiz_attempts.count()

    average_score = 0

    if total_quiz_attempts > 0:

        total_percentage = 0

        for result in quiz_attempts:

            if result.total_questions > 0:

                percentage = (
                    result.score
                    / result.total_questions
                ) * 100

                total_percentage += percentage

        average_score = int(
            total_percentage
            / total_quiz_attempts
        )

    return render(
        request,
        "staff_dashboard.html",
        {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_lessons": total_lessons,
            "total_quizzes": total_quizzes,
            "ai_quizzes": ai_quizzes,
            "total_quiz_attempts": total_quiz_attempts,
            "average_score": average_score,
            "students": students,
            "courses": courses,
            "lessons": lessons,
            "quizzes": quizzes,
            "quiz_attempts": quiz_attempts
        }
    )


@staff_member_required
def student_detail(request, user_id):

    from courses.models import Lesson, Progress, QuizResult

    student = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    total_lessons = Lesson.objects.count()

    completed_progress = Progress.objects.filter(
        user=student,
        completed=True
    ).select_related(
        "lesson"
    )

    completed_lessons = completed_progress.count()

    if total_lessons > 0:
        progress_percentage = int(
            (completed_lessons / total_lessons) * 100
        )
    else:
        progress_percentage = 0

    quiz_results = QuizResult.objects.filter(
        user=student
    ).select_related(
        "quiz"
    ).order_by(
        "-attempted_at"
    )

    total_quiz_attempts = quiz_results.count()

    average_score = 0
    best_score = 0

    if total_quiz_attempts > 0:

        total_percentage = 0

        for result in quiz_results:

            if result.total_questions > 0:

                percentage = (
                    result.score
                    / result.total_questions
                ) * 100

                total_percentage += percentage

                if percentage > best_score:
                    best_score = percentage

        average_score = int(
            total_percentage
            / total_quiz_attempts
        )

        best_score = int(best_score)

    if total_quiz_attempts == 0:
        performance_level = "No Quiz Attempted 📝"

    elif average_score < 50:
        performance_level = "Needs Improvement 📚"

    elif average_score < 80:
        performance_level = "Good Performance 👍"

    else:
        performance_level = "Excellent Performance 🏆"

    return render(
        request,
        "student_detail.html",
        {
            "student": student,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "completed_progress": completed_progress,
            "quiz_results": quiz_results,
            "total_quiz_attempts": total_quiz_attempts,
            "average_score": average_score,
            "best_score": best_score,
            "performance_level": performance_level
        }
    )