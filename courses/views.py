import os
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from openai import OpenAI

from .models import Course, Lesson, Progress, Quiz, Question, QuizResult


def course_list(request):

    courses = Course.objects.all()

    search_query = request.GET.get("search", "")
    difficulty = request.GET.get("difficulty", "")

    if search_query:
        courses = courses.filter(
            title__icontains=search_query
        )

    if difficulty:
        courses = courses.filter(
            difficulty=difficulty
        )

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
            "search_query": search_query,
            "difficulty": difficulty
        }
    )


def course_detail(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lessons = Lesson.objects.filter(
        course=course
    )

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "lessons": lessons
        }
    )


@login_required
def lesson_detail(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    quizzes = Quiz.objects.filter(
        lesson=lesson
    ).order_by("-id")

    quiz = quizzes.first()

    if request.method == "POST":

        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        return redirect(
            "lesson_detail",
            lesson_id=lesson.id
        )

    return render(
        request,
        "courses/lesson_detail.html",
        {
            "lesson": lesson,
            "progress": progress,
            "quiz": quiz,
            "quizzes": quizzes
        }
    )


@login_required
def quiz(request, quiz_id):

    quiz = get_object_or_404(
        Quiz,
        id=quiz_id
    )

    questions = Question.objects.filter(
        quiz=quiz
    )

    score = None
    percentage = None

    if request.method == "POST":

        score = 0

        total_questions = questions.count()

        for question in questions:

            selected_option = request.POST.get(
                "question_" + str(question.id)
            )

            if selected_option:

                if int(selected_option) == question.correct_option:

                    score += 1


        # Calculate percentage

        if total_questions > 0:

            percentage = round(
                (score / total_questions) * 100,
                2
            )

        else:

            percentage = 0


        # Save result

        QuizResult.objects.create(

            user=request.user,

            quiz=quiz,

            score=score,

            total_questions=total_questions

        )


    return render(

        request,

        "courses/quiz.html",

        {

            "quiz": quiz,

            "questions": questions,

            "score": score,

            "percentage": percentage

        }

    )



@login_required
def generate_ai_quiz(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    generated_questions = []
    error = ""

    if request.method == "POST":

        difficulty = request.POST.get(
            "difficulty",
            "Beginner"
        )

        question_count = request.POST.get(
            "question_count",
            "5"
        )

        try:

            question_count = int(question_count)

            if question_count < 1:
                question_count = 5

            if question_count > 10:
                question_count = 10

        except ValueError:

            question_count = 5

        try:

            hf_token = os.getenv("HF_TOKEN")

            if not hf_token:

                error = "Hugging Face token was not found."

            else:

                client = OpenAI(
                    base_url="https://router.huggingface.co/v1",
                    api_key=hf_token
                )

                prompt = f"""
                Create a multiple-choice quiz for a student.

                Topic:
                {lesson.title}

                Lesson content:
                {lesson.content}

                Difficulty:
                {difficulty}

                Number of questions:
                {question_count}

                Return ONLY valid JSON.

                The JSON must be an array.

                Each question must have exactly these fields:

                question
                option1
                option2
                option3
                option4
                correct_option

                correct_option must be a number:
                1, 2, 3 or 4.

                Example format:

                [
                    {{
                        "question": "What is Python?",
                        "option1": "A programming language",
                        "option2": "A database",
                        "option3": "An operating system",
                        "option4": "A browser",
                        "correct_option": 1
                    }}
                ]

                Do not add markdown.
                Do not add explanations.
                """

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b:fastest",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an AI quiz generator. "
                                "Return only valid JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                ai_response = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                ai_response = ai_response.strip()

                if ai_response.startswith("```"):

                    ai_response = ai_response.replace(
                        "```json",
                        ""
                    )

                    ai_response = ai_response.replace(
                        "```",
                        ""
                    )

                    ai_response = ai_response.strip()

                generated_questions = json.loads(
                    ai_response
                )

                quiz = Quiz.objects.create(
                    lesson=lesson,
                    title=(
                        "AI Generated Quiz - "
                        + lesson.title
                    ),
                    difficulty=difficulty,
                    is_ai_generated=True
                )

                for item in generated_questions:

                    Question.objects.create(
                        quiz=quiz,
                        question_text=item["question"],
                        option1=item["option1"],
                        option2=item["option2"],
                        option3=item["option3"],
                        option4=item["option4"],
                        correct_option=int(
                            item["correct_option"]
                        )
                    )

                return redirect(
                    "quiz",
                    quiz_id=quiz.id
                )

        except Exception as e:

            error = "Quiz generation failed: " + str(e)

    return render(
        request,
        "courses/ai_quiz_generator.html",
        {
            "lesson": lesson,
            "error": error
        }
    )


@staff_member_required
def manage_courses(request):

    courses = Course.objects.all().order_by("title")

    return render(
        request,
        "courses/manage_courses.html",
        {
            "courses": courses
        }
    )


@staff_member_required
def add_course(request):

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        instructor = request.POST.get("instructor")
        duration = request.POST.get("duration")
        difficulty = request.POST.get("difficulty")

        Course.objects.create(
            title=title,
            description=description,
            instructor=instructor,
            duration=duration,
            difficulty=difficulty
        )

        return redirect("manage_courses")

    return render(
        request,
        "courses/course_form.html",
        {
            "page_title": "Add Course"
        }
    )


@staff_member_required
def edit_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        course.instructor = request.POST.get("instructor")
        course.duration = request.POST.get("duration")
        course.difficulty = request.POST.get("difficulty")

        course.save()

        return redirect("manage_courses")

    return render(
        request,
        "courses/course_form.html",
        {
            "course": course,
            "page_title": "Edit Course"
        }
    )


@staff_member_required
def delete_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":
        course.delete()

    return redirect("manage_courses")


@staff_member_required
def manage_lessons(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lessons = Lesson.objects.filter(
        course=course
    ).order_by("title")

    return render(
        request,
        "courses/manage_lessons.html",
        {
            "course": course,
            "lessons": lessons
        }
    )


@staff_member_required
def add_lesson(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        video_url = request.POST.get("video_url")

        Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            video_url=video_url
        )

        return redirect(
            "manage_lessons",
            course_id=course.id
        )

    return render(
        request,
        "courses/lesson_form.html",
        {
            "course": course,
            "page_title": "Add Lesson"
        }
    )


@staff_member_required
def edit_lesson(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    if request.method == "POST":

        lesson.title = request.POST.get("title")
        lesson.content = request.POST.get("content")
        lesson.video_url = request.POST.get("video_url")

        lesson.save()

        return redirect(
            "manage_lessons",
            course_id=lesson.course.id
        )

    return render(
        request,
        "courses/lesson_form.html",
        {
            "lesson": lesson,
            "course": lesson.course,
            "page_title": "Edit Lesson"
        }
    )


@staff_member_required
def delete_lesson(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    course_id = lesson.course.id

    if request.method == "POST":
        lesson.delete()

    return redirect(
        "manage_lessons",
        course_id=course_id
    )