from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # AI TUTOR
    # =====================================================

    path(
        '',
        views.tutor_home,
        name='tutor_home'
    ),

    path(
        'clear/',
        views.clear_history,
        name='clear_chat_history'
    ),


    # =====================================================
    # QUIZ MANAGEMENT
    # =====================================================

    path(
        'quizzes/',
        views.quiz_list,
        name='quiz_list'
    ),

    path(
        'quizzes/add/',
        views.add_quiz,
        name='add_quiz'
    ),

    path(
        'quizzes/<int:quiz_id>/edit/',
        views.edit_quiz,
        name='edit_quiz'
    ),

    path(
        'quizzes/<int:quiz_id>/delete/',
        views.delete_quiz,
        name='delete_quiz'
    ),


    # =====================================================
    # QUESTION MANAGEMENT
    # =====================================================

    path(
        'quizzes/<int:quiz_id>/questions/',
        views.question_list,
        name='question_list'
    ),

    path(
        'quizzes/<int:quiz_id>/questions/add/',
        views.add_question,
        name='add_question'
    ),

    path(
        'questions/<int:question_id>/edit/',
        views.edit_question,
        name='edit_question'
    ),

    path(
        'questions/<int:question_id>/delete/',
        views.delete_question,
        name='delete_question'
    ),


    # =====================================================
    # AI QUIZ GENERATOR
    # =====================================================

    path(
        'quizzes/ai-generate/',
        views.generate_ai_quiz,
        name='generate_ai_quiz'
    ),

]