from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    instructor = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=50
    )

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        default="Beginner"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return self.title


class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    content = models.TextField()

    video_url = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return self.title


class Progress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )


    def __str__(self):

        return (
            self.user.username
            + " - "
            + self.lesson.title
        )


class Quiz(models.Model):
    lesson = models.ForeignKey(
    Lesson,
    on_delete=models.CASCADE
    )
    

    title = models.CharField(
        max_length=200
    )

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        default="Beginner"
    )

    is_ai_generated = models.BooleanField(
        default=False
    )


    def __str__(self):

        return self.title


class Question(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    question_text = models.CharField(
        max_length=500
    )

    option1 = models.CharField(
        max_length=200
    )

    option2 = models.CharField(
        max_length=200
    )

    option3 = models.CharField(
        max_length=200
    )

    option4 = models.CharField(
        max_length=200
    )

    correct_option = models.IntegerField()


    def __str__(self):

        return self.question_text


class QuizResult(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    score = models.IntegerField()

    total_questions = models.IntegerField()

    attempted_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return (
            self.user.username
            + " - "
            + self.quiz.title
            + " - "
            + str(self.score)
            + "/"
            + str(self.total_questions)
        )