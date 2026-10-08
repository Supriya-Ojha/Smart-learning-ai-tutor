from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.course_list,
        name='course_list'
    ),

    path(
        'lesson/<int:lesson_id>/',
        views.lesson_detail,
        name='lesson_detail'
    ),

    path(
        'lesson/<int:lesson_id>/generate-quiz/',
        views.generate_ai_quiz,
        name='generate_ai_quiz'
    ),

    path(
        'quiz/<int:quiz_id>/',
        views.quiz,
        name='quiz'
    ),

    path(
        'manage/',
        views.manage_courses,
        name='manage_courses'
    ),

    path(
        'manage/add/',
        views.add_course,
        name='add_course'
    ),

    path(
        'manage/edit/<int:course_id>/',
        views.edit_course,
        name='edit_course'
    ),

    path(
        'manage/delete/<int:course_id>/',
        views.delete_course,
        name='delete_course'
    ),

    path(
        'manage/<int:course_id>/lessons/',
        views.manage_lessons,
        name='manage_lessons'
    ),

    path(
        'manage/<int:course_id>/lessons/add/',
        views.add_lesson,
        name='add_lesson'
    ),

    path(
        'manage/lesson/<int:lesson_id>/edit/',
        views.edit_lesson,
        name='edit_lesson'
    ),

    path(
        'manage/lesson/<int:lesson_id>/delete/',
        views.delete_lesson,
        name='delete_lesson'
    ),

    path(
        '<int:course_id>/',
        views.course_detail,
        name='course_detail'
    ),
]